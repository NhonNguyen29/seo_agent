import os
import json
import sys
import math
import re
import logging
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Optional imports with graceful fallback
try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    HAS_TENACITY = True
except ImportError:
    HAS_TENACITY = False
    def retry(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import coloredlogs
    HAS_COLOREDLOGS = True
except ImportError:
    HAS_COLOREDLOGS = False

# Import config loader
try:
    from config_loader import load_config, validate_api_keys
except ImportError:
    # Fallback config loader
    def load_config(env_path=None):
        return {
            "SERPER_API_KEY": os.getenv("SERPER_API_KEY", "YOUR_SERPER_API_KEY"),
            "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", "YOUR_FIRECRAWL_API_KEY"),
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY"),
            "OUTPUT_DIR": os.getenv("OUTPUT_DIR", "outputs"),
            "LOG_DIR": os.getenv("LOG_DIR", "logs"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        }
    
    def validate_api_keys(config):
        return {
            "Serper": {"configured": "YOUR_" not in config.get("SERPER_API_KEY", "")},
            "Firecrawl": {"configured": "YOUR_" not in config.get("FIRECRAWL_API_KEY", "")},
            "OpenRouter": {"configured": "YOUR_" not in config.get("OPENROUTER_API_KEY", "")},
        }

# Setup logging
logger = logging.getLogger(__name__)

# =====================================================================
# CẤU HÌNH HỆ THỐNG
# =====================================================================
config = load_config()
SERPER_API_KEY = config.get("SERPER_API_KEY", "YOUR_SERPER_API_KEY")
FIRECRAWL_API_KEY = config.get("FIRECRAWL_API_KEY", "YOUR_FIRECRAWL_API_KEY")
OPENROUTER_API_KEY = config.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")
OUTPUT_DIR = config.get("OUTPUT_DIR", "outputs")
LOG_DIR = config.get("LOG_DIR", "logs")
LOG_LEVEL = config.get("LOG_LEVEL", "INFO")
RESEARCH_RESULTS_PER_KW = int(config.get("RESEARCH_RESULTS_PER_KW", "5"))
SCRAPER_MAX_PER_KEYWORD = int(config.get("SCRAPER_MAX_PER_KEYWORD", "3"))
SCRAPER_TIMEOUT = int(config.get("SCRAPER_TIMEOUT", "30"))
SCRAPER_DELAY = float(config.get("SCRAPER_DELAY", "1.0"))
SEMANTIC_SIMILARITY_THRESHOLD = float(config.get("SEMANTIC_SIMILARITY_THRESHOLD", "0.75"))
OUTLINE_MODEL = config.get("OUTLINE_MODEL", "openrouter/auto")
NLP_MODEL = config.get("NLP_MODEL", "vi_core_news_lg")
DOMAIN_KEYWORD_MODEL = config.get("DOMAIN_KEYWORD_MODEL", "openrouter/auto")
DOMAIN_KEYWORD_MAX_TOKENS = int(config.get("DOMAIN_KEYWORD_MAX_TOKENS", "1200"))
DOMAIN_KEYWORD_SUGGESTION_LIMIT = int(config.get("DOMAIN_KEYWORD_SUGGESTION_LIMIT", "20"))
DOMAIN_FETCH_TIMEOUT = int(config.get("DOMAIN_FETCH_TIMEOUT", "30"))

# Use sentence-transformers as the primary semantic engine (no spaCy dependency)
embedder = None
nlp = None
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Loaded SentenceTransformer embedder: all-MiniLM-L6-v2")
except Exception as e:
    embedder = None
    logger.warning(f"SentenceTransformer not available: {e}. Falling back to token-based similarity")


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging with optional file output."""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except:
        pass
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except:
            pass
    
    # Try to apply colored logs
    if HAS_COLOREDLOGS:
        try:
            coloredlogs.install(level=log_level.upper())
        except:
            pass


# Initialize logging
setup_logging(LOG_LEVEL)


# =====================================================================
# PIPELINE 1: MOBILE RESEARCH AGENT SKILL
# =====================================================================
class ResearchAgent:
    """
    Skill 1: Nghiên cứu thị trường Mobile tại Việt Nam sử dụng Serper.dev API.
    Giả lập thiết bị di động để bắt trọn Search Intent chuẩn Mobile-First Indexing.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://serper.dev"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)) if HAS_TENACITY else lambda f: f
    def _make_request(self, keyword: str) -> Dict[str, Any]:
        """Make Serper API request with retry logic."""
        if not HAS_REQUESTS:
            logger.warning("requests library not available; using simulated data")
            return {}
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "q": keyword,
            "gl": "vn",
            "hl": "vi",
            "device": "mobile",
            "num": RESEARCH_RESULTS_PER_KW
        })
        
        try:
            response = requests.post(self.url, headers=headers, data=payload, timeout=SCRAPER_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"API request failed: {e}")
            return {}

    def execute(self, keyword: str) -> Dict[str, Any]:
        logger.info(f"[Pipeline 1] Researching keyword (mobile): '{keyword}'")
        
        try:
            if self.api_key == "YOUR_SERPER_API_KEY":
                raise ValueError("Serper API key not configured. Using fallback data.")
            
            data = self._make_request(keyword)
            
            # Filter out YouTube URLs and get top 10 organic results
            urls = [item['link'] for item in data.get('organic', []) 
                   if 'link' in item and 'youtube.com' not in item['link'].lower()][:10]
            paa_questions = [item['question'] for item in data.get('peopleAlsoAsked', []) if 'question' in item]
            
            logger.info(f"Found {len(urls)} competitor URLs and {len(paa_questions)} 'People Also Ask' questions")
            return {"urls": urls, "questions": paa_questions}
        except Exception as e:
            logger.warning(f"API request failed: {e}. Using simulated data for demo.")
            return {
                "urls": [
                    "https://example-competitor-1.com",
                    "https://example-competitor-2.com",
                    "https://example-competitor-3.com"
                ],
                "questions": [
                    f"Làm sao để tối ưu {keyword}?",
                    f"Best practices cho {keyword}?",
                    f"{keyword} bao gồm những gì?"
                ]
            }


# =====================================================================
# DOMAIN KEYWORD ANALYSIS AGENT SKILL
# =====================================================================
class DomainKeywordAgent:
    """Skill: analyze a domain and generate keyword opportunities with OpenRouter."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def _clean_html(self, html: str) -> str:
        html = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', html)
        html = re.sub(r'(?s)<[^>]+>', ' ', html)
        html = re.sub(r'\s+', ' ', html).strip()
        return html[:4000]

    def _fetch_domain_text(self, domain: str) -> str:
        if not HAS_REQUESTS:
            logger.warning("requests library not available; using domain fallback text")
            return f"Website domain: {domain}"

        for scheme in ["https://", "http://"]:
            url = f"{scheme}{domain}"
            try:
                response = requests.get(url, timeout=DOMAIN_FETCH_TIMEOUT)
                response.raise_for_status()
                return self._clean_html(response.text)
            except Exception as e:
                logger.debug(f"Domain fetch failed for {url}: {e}")
        logger.warning(f"Unable to fetch domain homepage for {domain}. Using domain name only.")
        return f"Website domain: {domain}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)) if HAS_TENACITY else lambda f: f
    def _call_openrouter(self, messages: List[Dict]) -> str:
        if not HAS_REQUESTS:
            logger.warning("requests library not available; using fallback keyword suggestions")
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DOMAIN_KEYWORD_MODEL,
            "messages": messages,
            "max_tokens": DOMAIN_KEYWORD_MAX_TOKENS
        }
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=DOMAIN_FETCH_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            logger.warning(f"Domain keyword OpenRouter request failed: {e}")
            return ""

    def execute(self, domain: str, max_keywords: int = 20) -> Dict[str, Any]:
        logger.info(f"[Domain Keyword] Analyzing domain: {domain}")
        domain_text = self._fetch_domain_text(domain)
        prompt = (
            f"Bạn là chuyên gia SEO và Content Strategist Việt Nam có 10+ năm kinh nghiệm. "
            f"Phân tích website sau để đề xuất danh sách keyword phù hợp, nhóm chủ đề và ý tưởng bài viết:\n"
            f"Domain: {domain}\n"
            f"Nội dung trang chủ: {domain_text}\n\n"
            "Yêu cầu:\n"
            "1. Liệt kê tối đa {max_keywords} keyword short-tail và long-tail phù hợp với domain (ưu tiên keyword dành cho người Việt).\n"
            "2. Nhóm keyword theo chủ đề/cluster với đơn vị từng cluster là 3-5 keyword.\n"
            "3. Đánh giá search intent cho mỗi nhóm keyword (informational, commercial, transactional, navigational).\n"
            "4. Gợi ý 5 ý tưởng bài viết cao khả năng lên top, viết bằng tiếng Việt dễ hiểu.\n"
            "5. Trả về định dạng JSON hợp lệ gồm: keywords, clusters, article_ideas, search_intent.\n"
            "Lưu ý: Nội dung phải gần gũi với thói quen tìm kiếm của người Việt Nam."
        )

        try:
            if self.api_key == "YOUR_OPENROUTER_API_KEY":
                raise ValueError("OpenRouter API key not configured. Using fallback keyword suggestions.")
            raw = self._call_openrouter([
                {"role": "system", "content": "Bạn là một chuyên gia SEO và nghiên cứu từ khóa."},
                {"role": "user", "content": prompt}
            ])

            if not raw:
                raise ValueError("OpenRouter returned no result.")

            # Try direct JSON parse
            try:
                parsed = json.loads(raw)
                # If parsed contains expected keys, return
                if isinstance(parsed, dict) and 'keywords' in parsed:
                    return {"domain": domain, "analysis": parsed}
            except Exception:
                pass

            # Try to extract JSON blob from text
            m = re.search(r"(\{[\s\S]*\})", raw)
            if m:
                try:
                    parsed = json.loads(m.group(1))
                    if isinstance(parsed, dict) and 'keywords' in parsed:
                        return {"domain": domain, "analysis": parsed}
                except Exception:
                    pass

            # Heuristic parsing: extract lines and lists
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            keywords = []
            clusters = []
            article_ideas = []
            search_intent = ''

            # Look for sections by keywords
            for i, line in enumerate(lines):
                low = line.lower()
                # keywords lines often contain commas or numbered lists
                if 'keyword' in low or ('-' in line and len(line.split())<=6) or (',' in line and len(line.split(','))<=6):
                    # split by common separators
                    parts = re.split(r'[,:;-]\s*', line)
                    for p in parts:
                        p = p.strip(' -–•"')
                        if p and len(p) > 2 and len(p.split()) <= 6:
                            keywords.append(p)
                if 'cluster' in low or 'nhóm' in low or 'theme' in low:
                    # try to grab next few lines as cluster content
                    j = i+1
                    c_keywords = []
                    while j < min(i+6, len(lines)):
                        if lines[j].startswith('-') or ',' in lines[j]:
                            c_keywords.extend([x.strip(' -–•"') for x in re.split('[,;]', lines[j]) if x.strip()])
                        j += 1
                    if c_keywords:
                        clusters.append({"theme": line, "keywords": c_keywords})
                if 'idea' in low or 'ý tưởng' in low or 'gợi ý' in low:
                    # collect following lines as ideas
                    j = i+1
                    while j < min(i+10, len(lines)):
                        if len(lines[j]) > 10:
                            article_ideas.append(lines[j].strip(' -–•"'))
                        j += 1
                if 'intent' in low or 'search intent' in low or 'mục đích' in low or 'search' in low:
                    # try to set search_intent
                    if ':' in line:
                        search_intent = line.split(':',1)[1].strip()

            # fallback mapping if heuristics didn't find enough
            if not keywords:
                # try to find bullet lists anywhere that look like keywords
                for line in lines:
                    if line.startswith('-') or line.startswith('•'):
                        item = line.lstrip('-• ').strip()
                        if len(item.split()) <= 6:
                            keywords.append(item)

            keywords = list(dict.fromkeys([k for k in keywords if k]))[:max_keywords]
            if not clusters and keywords:
                clusters = [{"theme": "General", "keywords": keywords[:5]}]
            if not article_ideas:
                article_ideas = [f"Gợi ý bài viết: {k}" for k in (keywords[:3] if keywords else [domain])]
            if not search_intent:
                search_intent = "Thông tin / Điều hướng"

            return {
                "domain": domain,
                "analysis": {
                    "keywords": keywords,
                    "clusters": clusters,
                    "article_ideas": article_ideas,
                    "search_intent": search_intent
                }
            }
        except Exception as e:
            logger.warning(f"Domain keyword analysis failed: {e}. Using fallback keywords.")
            fallback_keywords = [
                f"{domain} marketing",
                f"dịch vụ {domain}",
                f"tối ưu {domain}",
                f"{domain} cho người mới",
                f"kinh nghiệm {domain}"
            ]
            return {
                "domain": domain,
                "analysis": {
                    "keywords": fallback_keywords[:max_keywords],
                    "clusters": [
                        {"theme": "Dịch vụ & giới thiệu", "keywords": [fallback_keywords[0], fallback_keywords[1]]},
                        {"theme": "Hướng dẫn", "keywords": [fallback_keywords[2], fallback_keywords[3]]}
                    ],
                    "article_ideas": [
                        f"Hướng dẫn đầy đủ về {domain} cho người mới bắt đầu",
                        f"Top 10 chiến lược SEO cho {domain}",
                        f"Bí quyết tối ưu hóa {domain} trên Google"
                    ],
                    "search_intent": "Thông tin, điều hướng và thương mại"
                }
            }


# =====================================================================
# PIPELINE 2: CONTENT SCRAPER AGENT SKILL
# =====================================================================
class ContentScraperAgent:
    """
    Skill 2: Cào dữ liệu bài viết đối thủ, bóc tách nội dung cốt lõi sang Markdown.
    Sử dụng Firecrawl API để vượt tường lửa và loại bỏ thành phần thừa (Menu, Ads).
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.firecrawl.dev/v1/scrape"

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5)) if HAS_TENACITY else lambda f: f
    def _scrape_url(self, url: str) -> Optional[str]:
        """Scrape single URL with retry logic."""
        if not HAS_REQUESTS:
            logger.warning("requests library not available; using simulated data")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True
        })
        
        try:
            response = requests.post(self.url, headers=headers, data=payload, timeout=SCRAPER_TIMEOUT)
            response.raise_for_status()
            res_data = response.json()
            return res_data.get('data', {}).get('markdown', '')
        except Exception as e:
            logger.warning(f"Scrape failed: {e}")
            return None

    def execute(self, target_urls: List[str]) -> List[str]:
        logger.info(f"[Pipeline 2] Scraping and cleaning content from {len(target_urls)} URLs")
        cleaned_contents = []
        
        for idx, url in enumerate(target_urls):
            logger.debug(f"Processing URL {idx+1}/{len(target_urls)}: {url}")
            try:
                if self.api_key == "YOUR_FIRECRAWL_API_KEY":
                    raise ValueError("Firecrawl API key not configured. Using simulated content.")
                
                markdown_content = self._scrape_url(url)
                if markdown_content:
                    cleaned_contents.append(markdown_content)
                    logger.debug(f"Successfully scraped {len(markdown_content)} characters from {url}")
                else:
                    logger.warning(f"No content extracted from {url}")
            except Exception as e:
                logger.warning(f"Scraping failed for {url}: {e}. Using simulated content.")
                simulated_markdown = f"# Bài viết từ {url}\n\n## Giới thiệu\n\nNội dung phân tích chuyên sâu về SEO mobile-first, tối ưu hóa trải nghiệm người dùng trên thiết bị di động, và chiến lược xây dựng thẩm quyền trong môi trường tìm kiếm hiện đại.\n\n## Phần nội dung chính\n\nBài viết này đề cập đến các khía cạnh quan trọng của SEO hiện đại bao gồm cấu trúc website, tối ưu hóa nội dung, và các yếu tố kỹ thuật ảnh hưởng đến xếp hạng."
                cleaned_contents.append(simulated_markdown)
            
            time.sleep(SCRAPER_DELAY)
        
        logger.info(f"Scraped {len(cleaned_contents)} documents")
        return cleaned_contents


# =====================================================================
# PIPELINE 3: SEMANTIC & DUPLICATE FILTER SKILL
# =====================================================================
class SemanticFilterAgent:
    """
    Skill 3: Lọc trùng lặp ngữ nghĩa sử dụng thuật toán Cosine Similarity bóc tách từ NLP.
    Đảm bảo nội dung định xây dựng có tính độc nhất (Unique Value), loại bỏ bài viết rác.
    """
    def __init__(self):
        pass

    def _get_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if nlp is None:
            # If embedder available, use embedding cosine similarity
            if embedder is not None:
                try:
                    v1 = embedder.encode(text1, convert_to_numpy=True)
                    v2 = embedder.encode(text2, convert_to_numpy=True)
                    # cosine similarity
                    denom = (math.sqrt((v1 * v1).sum()) * math.sqrt((v2 * v2).sum()))
                    if denom == 0:
                        return 0.0
                    return float((v1 @ v2) / denom)
                except Exception as e:
                    logger.warning(f"Embedder similarity failed: {e}")
            # Fallback: token-based Jaccard similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = words1.intersection(words2)
            if not words1 or not words2:
                return 0.0
            return len(intersection) / math.sqrt(len(words1) * len(words2))
        
        try:
            doc1 = nlp(text1[:2000])
            doc2 = nlp(text2[:2000])
            return doc1.similarity(doc2)
        except Exception as e:
            logger.warning(f"Error calculating NLP similarity: {e}. Using token similarity.")
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = words1.intersection(words2)
            if not words1 or not words2:
                return 0.0
            return len(intersection) / math.sqrt(len(words1) * len(words2))

    def execute(self, competitor_contents: List[str], base_topic: str) -> List[str]:
        logger.info(f"[Pipeline 3] Analyzing semantic duplicates (threshold: {SEMANTIC_SIMILARITY_THRESHOLD})")
        unique_points = []
        
        for idx, content in enumerate(competitor_contents):
            similarity_score = self._get_similarity(base_topic, content)
            logger.debug(f"Content {idx+1} similarity: {similarity_score*100:.2f}%")
            
            if similarity_score < SEMANTIC_SIMILARITY_THRESHOLD:
                unique_point = f"Unique insight from source {idx+1}: Deep content covering underexploited angles in the market."
                unique_points.append(unique_point)
                logger.debug(f"Content {idx+1} kept (below threshold)")
            else:
                logger.debug(f"Content {idx+1} filtered (above {SEMANTIC_SIMILARITY_THRESHOLD} threshold)")
        
        if not unique_points:
            unique_points.append(f"New angle: Focus on practical, user-centric optimization for mobile search in Vietnamese market.")
            logger.info("No unique content found; using fallback angle")
        
        logger.info(f"Found {len(unique_points)} unique content gaps")
        return unique_points


# =====================================================================
# PIPELINE 4: MASS OUTLINE GENERATOR SKILL
# =====================================================================
class OutlineGeneratorAgent:
    """
    Skill 4: Tích hợp OpenRouter Auto Router để chọn mô hình tốt nhất tự động,
    lập cấu trúc Outline và xuất nội dung chuẩn Google E-E-A-T cho Tiếng Việt.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)) if HAS_TENACITY else lambda f: f
    def _call_openrouter(self, messages: List[Dict]) -> str:
        """Call OpenRouter API with retry logic."""
        if not HAS_REQUESTS:
            logger.warning("requests library not available; using fallback outline")
            return ""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": OUTLINE_MODEL,
            "messages": messages,
            "max_tokens": int(config.get("OUTLINE_MAX_TOKENS", "2048"))
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=SCRAPER_TIMEOUT)
            response.raise_for_status()
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
        except Exception as e:
            logger.warning(f"API call failed: {e}")
            return ""

    def execute(self, keyword: str, questions: List[str], content_gaps: List[str], competitor_urls: Optional[List[str]] = None) -> str:
        logger.info(f"[Pipeline 4] Generating outline for: {keyword}")
        
        context_questions = "\n".join([f"- {q}" for q in questions[:5]])  # Limit to 5 questions
        context_gaps = "\n".join([f"- {gap}" for gap in content_gaps[:5]])  # Limit to 5 gaps
        
        competitor_note = ""
        if competitor_urls:
            urls_text = "\n".join([f"- {url}" for url in competitor_urls[:10]])
            competitor_note = (
                "Các URL cạnh tranh tham khảo (top 10 kết quả hữu cơ, đã loại trừ YouTube):\n"
                f"{urls_text}\n\n"
                "Lưu ý: không sao chép nguyên văn nội dung từ các URL này, chỉ dùng chúng làm tham khảo về cấu trúc chủ đề, giọng văn và ý chính."
            )
        
        system_prompt = (
            "Bạn là một chuyên gia SEO kỹ thuật bậc cao, copywriter chuyên nghiệp, am hiểu sâu sắc hệ thống Helpful Content của Google và tiêu chuẩn E-E-A-T.\n"
            "Bạn có kinh nghiệm viết nội dung SEO cho thị trường Việt Nam, hiểu rõ tâm lý và ngôn ngữ của độc giả Việt.\n"
            "Nhiệm vụ: lập một Outline bài viết bằng Markdown, chuyên nghiệp, gần gũi với người Việt, theo dữ liệu nghiên cứu được cung cấp.\n"
            "Yêu cầu:\n"
            "1. Direct Answer (100 từ đầu tiên): trả lời trực diện ý định tìm kiếm, dùng ngôn ngữ dễ hiểu của người Việt.\n"
            "2. Heading Hierarchy: H2, H3, H4 logic, không nhồi nhét từ khóa, cấu trúc dễ theo dõi.\n"
            "3. Semantic Entities: liệt kê ít nhất 5-7 thực thể cần có trong bài.\n"
            "4. Copy Writing từ content gap: Tách riêng nội dung độc quyền từ các khoảng trống (content gaps) đã xác định.\n"
            "5. Tính thực tế: Bao gồm ví dụ, case study, kinh nghiệm thực tế của thị trường Việt.\n"
            "6. Không sử dụng nội dung YouTube trong outline hoặc đề xuất từ khóa."
        )
        
        user_prompt = f"""
Từ khóa chính: {keyword}

Câu hỏi người dùng tìm kiếm (Search Intent):
{context_questions}

Khoảng trống nội dung cần khai thác (Content Gaps - copy từ top 10 URLs):
{context_gaps}

{competitor_note}
Hãy tạo Outline bài viết chuẩn SEO E-E-A-T bằng Tiếng Việt, sẵn sàng cho copywriter viết chi tiết.

Đặc biệt chú ý:
- Nội dung phải gần gũi, dễ hiểu với độc giả Việt Nam
- Sử dụng ví dụ, case study, kinh nghiệm thực tế từ thị trường Việt
- Tách rõ ràng nội dung độc quyền từ các content gaps
- Cấu trúc heading phải hợp lý, dễ theo dõi
"""
        
        try:
            if self.api_key == "YOUR_OPENROUTER_API_KEY":
                raise ValueError("OpenRouter API key not configured. Using fallback template.")
            
            logger.debug(f"Calling OpenRouter with model: {OUTLINE_MODEL}")
            outline_text = self._call_openrouter([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            logger.info(f"Outline generated successfully ({len(outline_text)} characters)")
            return outline_text
        except Exception as e:
            logger.warning(f"OpenRouter API failed: {e}. Using fallback template.")
            fallback_outline = f"""# Outline SEO E-E-A-T: {keyword}

## 1. Mở bài & Trả lời trực diện (Direct Answer)
Trong 100 từ đầu tiên, bài viết phải trả lời trực diện câu hỏi của người dùng:
- Định nghĩa {keyword}
- Tại sao {keyword} quan trọng với người dùng di động tại Việt Nam

## 2. Tìm hiểu bản chất nền tảng cốt lõi
- Khái niệm và định nghĩa chi tiết
- Ngữ cảnh ứng dụng hiện tại

## 3. Hướng dẫn chi tiết (How-to)
- Bước 1: [Action cụ thể]
- Bước 2: [Action cụ thể]
- Bước 3: [Action cụ thể]
- Checklist: Danh sách kiểm tra từng điểm

## 4. Ví dụ thực tế & Case Studies
- Ví dụ 1: Trích dẫn từ nguồn đáng tin cậy
- Ví dụ 2: Dữ liệu thực tế hoặc trường hợp nghiên cứu
- Ví dụ 3: Best practice từ industy leaders

## 5. Các câu hỏi thường gặp (FAQ)
- Q: [Câu hỏi]? A: [Trả lời ngắn, rõ ràng]
- Q: [Câu hỏi]? A: [Trả lời ngắn, rõ ràng]

## 6. Kết luận & Call-to-Action
- Tóm tắt điểm chính
- Hành động tiếp theo cho người dùng

## 7. Thực thể Semantic cần có
- Entity 1: [Tên thực thể]
- Entity 2: [Tên thực thể]
- Entity 3: [Tên thực thể]
- Entity 4: [Tên thực thể]
- Entity 5: [Tên thực thể]
"""
            return fallback_outline


def _ensure_out_dir(path: str = "outputs"):
    """Create output directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, "logs"), exist_ok=True)


def run_pipeline(keywords: List[str], out_dir: str = "outputs", steps: Optional[List[str]] = None):
    """Run full pipeline for a list of keywords.
    
    Args:
        keywords: List of keywords to process.
        out_dir: Output directory for results.
        steps: List of specific steps to run (all by default).
    """
    _ensure_out_dir(out_dir)
    
    # Validate API keys
    api_status = validate_api_keys(config)
    configured = sum(1 for s in api_status.values() if s['configured'])
    logger.info(f"API Status: {configured}/3 configured (fallback mode enabled)")
    
    research = ResearchAgent(SERPER_API_KEY)
    scraper = ContentScraperAgent(FIRECRAWL_API_KEY)
    semantic = SemanticFilterAgent()
    outline_gen = OutlineGeneratorAgent(OPENROUTER_API_KEY)

    for kw in keywords:
        logger.info(f"{'='*60}")
        logger.info(f"Processing keyword: {kw}")
        logger.info(f"{'='*60}")
        
        # Step 1: Research
        if not steps or "research" in steps:
            res = research.execute(kw)
            urls = res.get("urls", [])
            questions = res.get("questions", [])
            
            # Save research output
            research_file = os.path.join(out_dir, f"research_{kw.replace(' ', '_')}.json")
            with open(research_file, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=2)
            logger.info(f"Research output saved: {research_file}")
        else:
            logger.info("Skipping research step")
            continue
        
        # Step 2: Scraper
        if not steps or "scraper" in steps:
            contents = scraper.execute(urls)
        else:
            logger.info("Skipping scraper step")
            contents = []
        
        # Step 3: Filter
        if not steps or "filter" in steps:
            gaps = semantic.execute(contents, kw)
        else:
            logger.info("Skipping filter step")
            gaps = ["Default gap: Focus on unique value proposition"]
        
        # Step 4: Outline
        if not steps or "outline" in steps:
            outline_text = outline_gen.execute(kw, questions, gaps, urls)
            
            # Save outline
            safe_kw = "_".join(kw.split())
            outline_file = os.path.join(out_dir, f"outline_{safe_kw}.md")
            with open(outline_file, "w", encoding="utf-8") as f:
                f.write(outline_text)
            logger.info(f"Outline saved: {outline_file}")
        else:
            logger.info("Skipping outline step")
        
        time.sleep(1)
    
    logger.info(f"Pipeline complete! Results in: {os.path.abspath(out_dir)}")


def run_single_step(step: str, out_dir: str = "outputs", **kwargs):
    """Run a single pipeline step with given parameters."""
    _ensure_out_dir(out_dir)
    
    if step == "research":
        keyword = kwargs.get("keyword", "mobile SEO")
        agent = ResearchAgent(SERPER_API_KEY)
        result = agent.execute(keyword)
        output_file = os.path.join(out_dir, f"research_{keyword.replace(' ', '_')}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Research result saved: {output_file}")
        
    elif step == "scraper":
        urls = kwargs.get("urls", ["https://example.com"])
        agent = ContentScraperAgent(FIRECRAWL_API_KEY)
        result = agent.execute(urls)
        output_file = os.path.join(out_dir, "raw_documents.jsonl")
        with open(output_file, "w", encoding="utf-8") as f:
            for doc in result:
                f.write(json.dumps({"content": doc[:500]}, ensure_ascii=False) + "\n")
        logger.info(f"Scraper result saved: {output_file}")
        
    elif step == "filter":
        documents = kwargs.get("documents", ["sample document"])
        base_topic = kwargs.get("topic", "SEO")
        agent = SemanticFilterAgent()
        result = agent.execute(documents, base_topic)
        output_file = os.path.join(out_dir, "filtered_gaps.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"gaps": result}, f, ensure_ascii=False, indent=2)
        logger.info(f"Filter result saved: {output_file}")
        
    elif step == "outline":
        keyword = kwargs.get("keyword", "SEO")
        questions = kwargs.get("questions", ["What is SEO?"])
        gaps = kwargs.get("gaps", ["Default gap"])
        agent = OutlineGeneratorAgent(OPENROUTER_API_KEY)
        result = agent.execute(keyword, questions, gaps)
        output_file = os.path.join(out_dir, f"outline_{keyword.replace(' ', '_')}.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        logger.info(f"Outline saved: {output_file}")


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="SEO Agent Pipeline - Automated keyword research & outline generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with demo keywords
  python seo_agent_tool.py --run-demo

  # Run pipeline with custom keywords
  python seo_agent_tool.py --keywords "mobile SEO" "PWA optimization"

  # Run single pipeline step
  python seo_agent_tool.py --step research --keyword "mobile SEO"

  # Custom output directory
  python seo_agent_tool.py --keywords "SEO" --out ./my_results

  # Debug mode
  python seo_agent_tool.py --keywords "SEO" --log-level DEBUG
        """
    )
    
    parser.add_argument("--keywords", "-k", nargs="+", help="Keywords to research and outline")
    parser.add_argument("--domain", help="Domain to analyze and generate keyword opportunities")
    parser.add_argument("--run-demo", action="store_true", help="Run demo with sample keywords")
    parser.add_argument("--step", choices=["research", "scraper", "filter", "outline"], 
                        help="Run only a specific pipeline step")
    parser.add_argument("--keyword", help="Single keyword for --step mode")
    parser.add_argument("--urls", nargs="+", help="URLs for scraper step")
    parser.add_argument("--documents", nargs="+", help="Documents for filter step")
    parser.add_argument("--topic", help="Base topic for filter step")
    parser.add_argument("--questions", nargs="+", help="Questions for outline step")
    parser.add_argument("--gaps", nargs="+", help="Content gaps for outline step")
    parser.add_argument("--out", default="outputs", help="Output directory (default: outputs)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level")
    
    args = parser.parse_args()
    
    # Setup logging with user's chosen level
    setup_logging(args.log_level, os.path.join(args.out, "logs", "pipeline.log"))
    
    logger.info("SEO Agent Pipeline started")
    logger.debug(f"Config loaded: {dict(config)}")
    
    if args.step:
        # Single step mode
        step_kwargs = {
            "keyword": args.keyword,
            "urls": args.urls or ["https://example.com"],
            "documents": args.documents or ["sample document"],
            "topic": args.topic,
            "questions": args.questions or ["What is this?"],
            "gaps": args.gaps or ["Default gap"]
        }
        run_single_step(args.step, args.out, **step_kwargs)
    elif args.run_demo:
        # Demo mode
        demo_keywords = ["mobile SEO best practices", "Progressive Web App optimization"]
        logger.info(f"Running demo with keywords: {demo_keywords}")
        run_pipeline(demo_keywords, args.out)
    elif args.domain:
        # Domain keyword discovery mode
        logger.info(f"Running domain keyword analysis for: {args.domain}")
        agent = DomainKeywordAgent(OPENROUTER_API_KEY)
        result = agent.execute(args.domain, max_keywords=DOMAIN_KEYWORD_SUGGESTION_LIMIT)
        os.makedirs(args.out, exist_ok=True)
        output_file = os.path.join(args.out, f"domain_keywords_{args.domain.replace('.', '_')}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Domain keyword analysis saved: {output_file}")
    elif args.keywords:
        # Full pipeline with custom keywords
        logger.info(f"Running pipeline with keywords: {args.keywords}")
        run_pipeline(args.keywords, args.out)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

## 2. Tìm hiểu bản chất nền tảng cốt lõi (H2)

# SEO Agent Pipeline — Công cụ tự động nghiên cứu & lên outline bài viết SEO

**Giới thiệu**: Hệ thống tự động 4 bước cho nghiên cứu SEO chuẩn Google E-E-A-T, từ keyword research (mobile Vietnam) → scrape content → filter semantic duplicates → generate article outlines.

---

## 📋 Tính năng chính

- **Pipeline 1 — Mobile Research**: Tìm kiếm SERP trên Serper.dev (giả lập device Mobile, locale VN) để lấy top competitors + "People Also Ask" questions.
- **Pipeline 2 — Content Scraper**: Cào nội dung từ các URL rivals bằng Firecrawl API (hoặc fallback simulated) → markdown.
- **Pipeline 3 — Semantic Deduplication**: Phân tích ngữ nghĩa + lọc nội dung trùng lặp dùng NLP (spaCy) hoặc token similarity.
- **Pipeline 4 — Outline Generator**: Tạo outline bài viết EEAT-compliant (H2/H3 structure, semantic entities, direct answer) qua OpenRouter `openrouter/auto` để tự động điều hướng model tốt nhất cho Tiếng Việt.

---

## 🚀 Quick Start

### 1. Cài đặt dependencies

```bash
cd /home/saoviet2026/ZCode/seo_agent_pipeline_project
pip install -r requirements.txt
```

**Optional**: Tải mô hình NLP Tiếng Việt để deduplication chính xác hơn:
```bash
python -m spacy download vi_core_news_lg
```

### 2. Cấu hình API Keys

Tạo file `.env` trong project root:

```bash
cp config.example.env .env
```

Sau đó mở `.env` và điền các API keys:

```env
SERPER_API_KEY=your_serper_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**Lưu ý**: Nếu không có API key, tool sẽ chạy ở chế độ dự phòng (fallback) với dữ liệu mẫu.

### 3. Chạy pipeline

**Demo mode** (với sample keywords):
```bash
python seo_agent_tool.py --run-demo
```

**Với keywords của bạn**:
```bash
python seo_agent_tool.py --keywords "mobile SEO best practices" "PWA performance optimization" --out ./my_outlines
```

**Chạy riêng từng step** (Advanced):
```bash
python seo_agent_tool.py --step research --keyword "mobile SEO" --out ./outputs
python seo_agent_tool.py --step scraper --urls urls.json --out ./outputs
python seo_agent_tool.py --step filter --documents docs.jsonl --topic "mobile SEO" --out ./outputs
python seo_agent_tool.py --step outline --keyword "mobile SEO" --questions questions.json --gaps gaps.json --out ./outputs
```

---

## 📁 Cấu trúc thư mục

```
seo_agent_pipeline_project/
├── seo_agent_tool.py              # Main pipeline orchestrator
├── config.example.env              # Template for .env config
├── .env                            # (Generated) Your actual API keys
├── requirements.txt                # Python dependencies
│
├── pipeline_01_research.md         # Tech spec: Mobile Research step
├── pipeline_02_scraper.md          # Tech spec: Content Scraper step
├── pipeline_03_filter.md           # Tech spec: Semantic Filter step
├── pipeline_04_outline.md          # Tech spec: Outline Generator step
├── README.md                       # This file
│
├── outputs/                        # (Auto-created) Output directory
│   ├── keywords_enriched.json
│   ├── raw_documents.jsonl
│   ├── documents_deduped.jsonl
│   └── outline_*.md
│
└── logs/                           # (Auto-created) Execution logs
    └── pipeline_*.log
```

---

## 🔧 Configuration & Customization

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SERPER_API_KEY` | Serper.dev API key for SERP research | `YOUR_SERPER_API_KEY` | Yes (for real SERP data) |
| `FIRECRAWL_API_KEY` | Firecrawl API key for content scraping | `YOUR_FIRECRAWL_API_KEY` | Yes (for real scraping) |
| `OPENROUTER_API_KEY` | OpenRouter API key for outline generation | `YOUR_OPENROUTER_API_KEY` | Yes (for LLM outlines) |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `OUTPUT_DIR` | Output directory for results | `./outputs` | No |

### Tuning Parameters (in `seo_agent_tool.py`)

```python
# Research step
RESEARCH_RESULTS_PER_KW = 5  # Top N competitors to fetch

# Scraper step
SCRAPER_MAX_PER_KEYWORD = 3  # How many URLs to scrape per keyword

# Filter step
SEMANTIC_SIMILARITY_THRESHOLD = 0.75  # Threshold for duplicate detection

# Outline step
OUTLINE_MODEL = "openrouter/auto"  # Use OpenRouter Auto Router for best routing
DOMAIN_KEYWORD_MODEL = "openrouter/auto"  # Use OpenRouter Auto Router for domain keyword analysis
```

---

## 📊 Output Examples

### Outline Output (sample)

```markdown
# Chiến lược Outline chuẩn SEO E-E-A-T: mobile SEO best practices

## 1. Mở bài & Trả lời trực diện (Direct Answer)
- Google mobile-first indexing prioritizes mobile UX...
- This means [100 words direct answer]

## 2. Tìm hiểu bản chất nền tảng cốt lõi
- Mobile-First Indexing definition
- Why Google switched to mobile-first

## 3. Hướng dẫn chi tiết / How-to
### 3.1 Site Speed Optimization
- Optimize images (WebP, lazy loading)
- Minimize CSS/JS
### 3.2 Mobile UX Best Practices
- Responsive design
- Touch-friendly buttons

## 4. Ví dụ thực tế
- Case study: [site A] improved from [X] to [Y]

## 5. FAQ
- Q: How to test mobile readiness? A: Use Mobile-Friendly Test

## 6. Semantic Entities
- Mobile-First Indexing, PageSpeed, Core Web Vitals, EEAT
```

---

## 🛠️ API Integration Details

### Serper.dev (Pipeline 1)

- **Endpoint**: `POST https://serper.dev`
- **Payload**:
  ```json
  {
    "q": "keyword",
    "gl": "vn",
    "hl": "vi",
    "device": "mobile",
    "num": 5
  }
  ```
- **Fallback**: Simulated SERP data if API key missing.

### Firecrawl (Pipeline 2)

- **Endpoint**: `POST https://firecrawl.dev`
- **Features**: JavaScript rendering, Cloudflare bypass, main content extraction.
- **Fallback**: BeautifulSoup-based basic scraping + simulated markdown.

### OpenRouter (Pipeline 4)

- **Endpoint**: `POST https://openrouter.ai`
- **Models**:
  - Primary: `deepseek/deepseek-r1:free` (reasoning + structure)
  - Secondary: `anthropic/claude-3.5-sonnet` (localization + polish)
- **Fallback**: Template-based outline if API key missing.

---

## ⚠️ Important Notes & Best Practices

### 1. Robots.txt & Legal Compliance

- **Always** check `robots.txt` before scraping a domain.
- **Respect** rate limits (add delays between requests).
- **Never** republish copyrighted content verbatim.

### 2. Cost Optimization

- **Serper API**: ~$0.01 per request. Use demo mode to test.
- **Firecrawl API**: ~$0.05–0.1 per page. Batch requests.
- **OpenRouter**: Variable by model. Use free/cheap models first (DeepSeek-R1).

### 3. Error Handling

- All steps have fallback modes (simulated data).
- Check logs in `./logs/` for detailed error messages.
- Use `--log-level DEBUG` for troubleshooting.

### 4. Performance

- Scraping multiple URLs is slower (async recommended for production).
- Embedding generation can take time; cache results for reuse.
- Pipeline typically completes in **2–5 minutes** per keyword (with real APIs).

---

## 📚 Pipeline Architecture

```
Keyword Input
    ↓
[Pipeline 1: Research] → SERP data + PAA questions
    ↓
[Pipeline 2: Scraper] → Raw HTML → Markdown content
    ↓
[Pipeline 3: Filter] → Semantic similarity → Unique content gaps
    ↓
[Pipeline 4: Outline Generator] → LLM-powered outline (EEAT)
    ↓
Output: Markdown outline ready for copywriter
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key missing" | Fill `.env` with real keys, or run in demo mode |
| Scraper returns empty | Check URL accessibility, Cloudflare status |
| Similarity scores all 1.0 | Install spaCy model: `python -m spacy download vi_core_news_lg` |
| Outline generation slow | Use cheaper OpenRouter model or smaller context |
| Rate limiting errors | Add delays between requests; use proxy rotation (advanced) |

---

## 🚀 Advanced Usage

### Batch Processing

Create a file `keywords.txt`:
```
mobile SEO best practices
progressive web app SEO
core web vitals optimization
```

Run batch mode:
```bash
cat keywords.txt | while read kw; do python seo_agent_tool.py --keywords "$kw"; done
```

### Custom Prompting (Pipeline 4)

Edit the `system_prompt` and `user_prompt` inside `OutlineGeneratorAgent.execute()` to customize outline style.

### Integration with Other Tools

Export outputs to:
- **JSON**: Use `--output-format json` for programmatic access.
- **Google Sheets**: Add a post-processor to push results to Sheets API.
- **Notion**: Integrate with Notion API for collaborative outline review.

---

## 📖 References

- [Google E-E-A-T Guide](https://developers.google.com/search/docs/appearance/helpful-content-system)
- [Mobile-First Indexing](https://developers.google.com/search/mobile-sites/mobile-first-indexing)
- [Serper API Docs](https://serper.dev/docs)
- [Firecrawl Docs](https://www.firecrawl.dev/)
- [OpenRouter Models](https://openrouter.ai/)
- [Semantic SEO Best Practices](https://www.semrush.com/blog/semantic-seo/)

---

## 📝 License & Disclaimer

This tool is provided as-is for educational and legitimate SEO research purposes. Users are responsible for:
- Complying with website ToS and robots.txt.
- Respecting copyright and data privacy laws.
- Managing API costs and rate limits.

---

## 💡 Contributing & Feedback

Found a bug? Want to add features? Submit issues or PRs to improve this tool!

**Questions?** Refer to the pipeline spec files (`pipeline_0X_*.md`) for technical details.

---

**Last Updated**: 2026-07-03  
**Version**: 1.0

#!/usr/bin/env python3
"""
SEO Agent Pipeline — Web GUI (Zero Dependencies)
================================================
Lightweight HTTP server for viewing SEO results - No Flask needed!

Usage:
    python3 seo_gui.py
    Then open: http://localhost:8000
"""

import os
import json
import subprocess
import threading
import argparse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from datetime import datetime

# ====================================================================
# Configuration
# ====================================================================

APP_DIR = Path(__file__).parent
OUTPUT_DIR = APP_DIR / "outputs"
DEFAULT_PORT = 8000
PORT = int(os.getenv('SEO_GUI_PORT', DEFAULT_PORT))

# Background tasks registry for long-running operations (domain analysis)
BACKGROUND_TASKS = {}

class ReuseAddrHTTPServer(HTTPServer):
    allow_reuse_address = True

# ====================================================================
# HTML Template
# ====================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Agent Pipeline GUI</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --success: #16a34a;
            --warning: #ea580c;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px 0;
        }
        
        .navbar {
            background: rgba(31, 41, 55, 0.95) !important;
            border-bottom: 3px solid var(--primary);
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            background: linear-gradient(45deg, var(--primary), #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .container-main {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header-section {
            background: linear-gradient(135deg, var(--primary), #06b6d4);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        .header-section h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .content-section {
            padding: 40px;
        }
        
        .tab-nav {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #f3f4f6;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            background: transparent;
            border: none;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            color: #6b7280;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .tab-btn.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .file-card {
            background: #f3f4f6;
            border-left: 4px solid var(--primary);
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-card:hover {
            background: #e5e7eb;
            transform: translateX(5px);
        }
        
        .file-card h5 {
            margin: 0 0 5px 0;
            color: #1f2937;
            font-weight: 600;
        }
        
        .file-content {
            background: #1f2937;
            color: #e5e7eb;
            padding: 20px;
            border-radius: 8px;
            max-height: 500px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            margin-top: 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
            display: none;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--primary), #06b6d4);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-card .number {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .stat-card .label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .form-section {
            background: #f3f4f6;
            padding: 30px;
            border-radius: 12px;
        }
        
        .btn-primary-custom {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary-custom:hover {
            background: #1d4ed8;
            color: white;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-brain"></i> SEO Agent Pipeline
            </a>
            <span class="navbar-text text-light">
                <i class="fas fa-check-circle text-success"></i> v1.0
            </span>
        </div>
    </nav>
    
    <!-- Main Container -->
    <div class="container mt-5 mb-5">
        <div class="container-main">
            <!-- Header -->
            <div class="header-section">
                <h1><i class="fas fa-chart-line"></i> SEO Outline Generator</h1>
                <p>Xem, quản lý và tạo bài viết SEO E-E-A-T</p>
            </div>
            
            <!-- Content -->
            <div class="content-section">
                <!-- Stats -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="number" id="outline-count">0</div>
                        <div class="label">Outlines</div>
                    </div>
                    <div class="stat-card">
                        <div class="number" id="research-count">0</div>
                        <div class="label">Research</div>
                    </div>
                    <div class="stat-card">
                        <div class="number" id="total-count">0</div>
                        <div class="label">Total Files</div>
                    </div>
                </div>
                
                <!-- Tabs -->
                <div class="tab-nav">
                    <button class="tab-btn active" onclick="switchTab(event, 'dashboard')">
                        <i class="fas fa-home"></i> Dashboard
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'outlines')">
                        <i class="fas fa-file-alt"></i> Outlines
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'research')">
                        <i class="fas fa-search"></i> Research
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'run')">
                        <i class="fas fa-play"></i> Run Pipeline
                    </button>
                        <button class="tab-btn" onclick="switchTab(event, 'domain')">
                            <i class="fas fa-network-wired"></i> Domain
                        </button>
                </div>
                
                <!-- Dashboard Tab -->
                <div id="dashboard" class="tab-content active">
                    <h3>📊 Dashboard</h3>
                    <p>Chào mừng đến với SEO Agent Pipeline GUI!</p>
                    <p>Công cụ này giúp bạn:</p>
                    <ul>
                        <li><strong>Xem Outlines:</strong> Các bài viết outline E-E-A-T</li>
                        <li><strong>Xem Research:</strong> Dữ liệu SERP và content analysis</li>
                        <li><strong>Chạy Pipeline:</strong> Tạo outline mới với keywords tùy ý</li>
                    </ul>
                </div>
                
                <!-- Outlines Tab -->
                <div id="outlines" class="tab-content">
                    <h3><i class="fas fa-file-alt"></i> Outlines</h3>
                    <div id="outlines-list">
                        <p style="text-align: center; color: #6b7280;">
                            <i class="fas fa-spinner fa-spin"></i> Đang tải...
                        </p>
                    </div>
                </div>
                
                <!-- Research Tab -->
                <div id="research" class="tab-content">
                    <h3><i class="fas fa-search"></i> Research Data</h3>
                    <div id="research-list">
                        <p style="text-align: center; color: #6b7280;">
                            <i class="fas fa-spinner fa-spin"></i> Đang tải...
                        </p>
                    </div>
                </div>
                
                <!-- Run Tab -->
                <div id="run" class="tab-content">
                    <h3><i class="fas fa-play"></i> Chạy Pipeline</h3>
                    <div class="form-section">
                        <form id="run-form">
                            <div class="mb-3">
                                <label for="keywords"><i class="fas fa-keyboard"></i> Keywords</label>
                                <input type="text" class="form-control" id="keywords" name="keywords" 
                                       placeholder="Ví dụ: mobile SEO, PWA optimization"
                                       required>
                                <small class="text-muted">Cách nhau bằng dấu phẩy</small>
                            </div>
                            <button type="submit" class="btn-primary-custom">
                                <i class="fas fa-rocket"></i> Chạy Pipeline
                            </button>
                        </form>
                        <div id="run-result" style="margin-top: 20px;"></div>
                    </div>
                </div>
                
                <!-- Domain Tab -->
                <div id="domain" class="tab-content">
                    <h3><i class="fas fa-network-wired"></i> Domain Analysis</h3>
                    <div class="form-section">
                        <form id="domain-form">
                            <div class="mb-3">
                                <label for="domain"><i class="fas fa-globe"></i> Domain</label>
                                <input type="text" class="form-control" id="domain" name="domain" placeholder="Ví dụ: blogdaytinhoc.com" required>
                            </div>
                            <button type="submit" class="btn-primary-custom">
                                <i class="fas fa-search"></i> Phân tích Domain
                            </button>
                        </form>
                        <div id="domain-result" style="margin-top: 20px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    <script>
        function switchTab(event, tabName) {
            event.preventDefault();
            // Hide all
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            // Show selected
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Load data
            if (tabName === 'outlines') loadOutlines();
            if (tabName === 'research') loadResearch();
            if (tabName === 'domain') loadDomain();
        }
        
        function loadOutlines() {
            fetch('/api/outlines')
                .then(r => r.json())
                .then(data => {
                    const html = data.files.length > 0
                        ? data.files.map(f => `
                            <div class="file-card" onclick="toggleContent(this)">
                                <h5><i class="fas fa-file-alt"></i> ${f.name}</h5>
                                <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">${f.size} KB | Click để xem</p>
                                <div class="file-content">${f.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
                            </div>
                        `).join('')
                        : '<p style="text-align: center; color: #6b7280;">Không có outlines</p>';
                    document.getElementById('outlines-list').innerHTML = html;
                });
        }
        
        function loadResearch() {
            fetch('/api/research')
                .then(r => r.json())
                .then(data => {
                    const html = data.files.length > 0
                        ? data.files.map(f => `
                            <div class="file-card" onclick="toggleContent(this)">
                                <h5><i class="fas fa-database"></i> ${f.name}</h5>
                                <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">${f.size} KB | Click để xem</p>
                                <div class="file-content">${f.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
                            </div>
                        `).join('')
                        : '<p style="text-align: center; color: #6b7280;">Không có research data</p>';
                    document.getElementById('research-list').innerHTML = html;
                });
        }
        
        function toggleContent(element) {
            const content = element.querySelector('.file-content');
            if (content) {
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
            }
        }
        
        function updateStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('outline-count').textContent = data.outline_count;
                    document.getElementById('research-count').textContent = data.research_count;
                    document.getElementById('total-count').textContent = data.total_count;
                });
        }
        
        document.getElementById('run-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const keywords = document.getElementById('keywords').value;
            const resultDiv = document.getElementById('run-result');
            resultDiv.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Đang chạy pipeline...</p>';
            
            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({keywords})
                });
                const data = await response.json();
                resultDiv.innerHTML = `<p style="color: green;"><i class="fas fa-check"></i> ${data.message}</p>`;
                setTimeout(() => { loadOutlines(); loadResearch(); updateStats(); }, 2000);
            } catch (err) {
                resultDiv.innerHTML = `<p style="color: red;"><i class="fas fa-times"></i> Lỗi: ${err.message}</p>`;
            }
        });
        
        async function analyzeDomain(domain) {
            const resultDiv = document.getElementById('domain-result');
            resultDiv.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Đang phân tích domain...</p>';
            try {
                const resp = await fetch('/api/domain', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({domain})
                });
                const data = await resp.json();
                // Start polling for result
                pollDomainResult(domain);
                return data;
            } catch (err) {
                resultDiv.innerHTML = `<p style="color: red;"><i class="fas fa-times"></i> Lỗi: ${err.message}</p>`;
            }
        }

        async function pollDomainResult(domain, tries=0) {
            const resultDiv = document.getElementById('domain-result');
            try {
                const q = new URLSearchParams({domain});
                const resp = await fetch('/api/domain?'+q.toString());
                const data = await resp.json();
                if (data.ready) {
                    renderDomainResult(data.payload);
                } else {
                    if (tries > 30) {
                        resultDiv.innerHTML = '<p style="color: red;">Timeout: Không có phản hồi từ phân tích domain.</p>';
                        return;
                    }
                    setTimeout(() => pollDomainResult(domain, tries+1), 2000);
                }
            } catch (err) {
                resultDiv.innerHTML = `<p style="color: red;"><i class="fas fa-times"></i> Lỗi: ${err.message}</p>`;
            }
        }

        function renderDomainResult(data) {
            const resultDiv = document.getElementById('domain-result');
            if (!data || !data.analysis) {
                resultDiv.innerHTML = '<p>Không có kết quả.</p>';
                return;
            }
            const {keywords, clusters, article_ideas, search_intent} = data.analysis;
            let html = `<h5>Kết quả cho <strong>${data.domain}</strong></h5>`;
            html += `<p><strong>Search intent:</strong> ${search_intent || ''}</p>`;
            html += '<div style="margin-top:10px;"><strong>Keywords</strong><div>';
            html += '<form id="selected-keywords-form">';
            html += keywords.map(k=>`<div class="form-check"><input class="form-check-input" type="checkbox" value="${k}" id="kw_${k.replace(/[^a-zA-Z0-9]/g,'_')}"> <label class="form-check-label" for="kw_${k.replace(/[^a-zA-Z0-9]/g,'_')}">${k}</label></div>`).join('');
            html += '</form></div>';
            if (clusters && clusters.length) {
                html += '<div style="margin-top:12px;"><strong>Clusters</strong><ul>' + clusters.map(c=>`<li><strong>${c.theme}:</strong> ${c.keywords.join(', ')}</li>`).join('') + '</ul></div>';
            }
            if (article_ideas && article_ideas.length) {
                html += '<div style="margin-top:12px;"><strong>Article ideas</strong><ul>' + article_ideas.map(a=>`<li>${a}</li>`).join('') + '</ul></div>';
            }
            html += `<div style="margin-top:12px;"><button class="btn-primary-custom" onclick="generateFromSelectedKeywords()">Tạo outlines từ keywords đã chọn</button> <button class="btn-primary-custom" style="margin-left:8px;" onclick="exportDomainCSV('${data.domain}')">Xuất CSV</button></div>`;
            resultDiv.innerHTML = html;
        }

        function loadDomain() {
            // Placeholder: clear previous result area
            document.getElementById('domain-result').innerHTML = '<p style="color:#6b7280;">Nhập domain và nhấn "Phân tích Domain" để bắt đầu.</p>';
            document.getElementById('domain-form')?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const domain = document.getElementById('domain').value.trim();
                if (!domain) return;
                await analyzeDomain(domain);
            });
        }

        function generateFromSelectedKeywords() {
            const checked = Array.from(document.querySelectorAll('#selected-keywords-form input[type=checkbox]:checked')).map(i=>i.value);
            if (!checked.length) {
                alert('Vui lòng chọn ít nhất 1 keyword');
                return;
            }
            // Reuse existing run endpoint
            fetch('/api/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({keywords: checked.join(',')})
            }).then(r=>r.json()).then(d=>{
                alert(d.message || 'Pipeline started');
                setTimeout(()=>{ loadOutlines(); loadResearch(); updateStats(); }, 3000);
            }).catch(err=>alert('Lỗi: '+err.message));
        }

        function exportDomainCSV(domain) {
            const q = new URLSearchParams({type: 'domain_keywords', domain});
            // trigger file download
            window.location = '/api/export?' + q.toString();
        }

        // Initial load
        updateStats();
        loadOutlines();
    </script>
</body>
</html>
"""

# ====================================================================
# HTTP Request Handler
# ====================================================================

class SEOGUIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for SEO GUI"""
    
    def do_GET(self):
        """Handle GET requests"""
        # support query strings for some endpoints
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
            
        elif path == '/api/outlines':
            self.send_json_response(self.get_outlines_data())
        elif path == '/api/research':
            self.send_json_response(self.get_research_data())
        elif path == '/api/stats':
            self.send_json_response(self.get_stats_data())
        elif path == '/api/export':
            qs = urllib.parse.parse_qs(parsed.query)
            typ = qs.get('type', [''])[0]
            domain = qs.get('domain', [''])[0]
            if typ == 'domain_keywords' and domain:
                fname = f"domain_keywords_{''.join([c if c.isalnum() else '_' for c in domain])}.json"
                fpath = OUTPUT_DIR / fname
                if not fpath.exists():
                    self.send_error(404, "Domain keywords not found")
                    return
                try:
                    with open(fpath, 'r', encoding='utf-8') as fp:
                        payload = json.load(fp)
                    # build CSV
                    import csv
                    from io import StringIO
                    sio = StringIO()
                    writer = csv.writer(sio)
                    writer.writerow(['domain', 'keyword', 'cluster', 'article_idea', 'search_intent'])
                    domain_v = payload.get('domain', domain)
                    analysis = payload.get('analysis', {})
                    kws = analysis.get('keywords', [])
                    clusters = analysis.get('clusters', [])
                    ideas = analysis.get('article_ideas', [])
                    intent = analysis.get('search_intent', '')
                    # Map cluster keywords to cluster name
                    cluster_map = {}
                    for c in clusters:
                        for k in c.get('keywords', []):
                            cluster_map[k] = c.get('theme')

                    max_rows = max(len(kws), len(ideas))
                    for i in range(max_rows):
                        k = kws[i] if i < len(kws) else ''
                        cl = cluster_map.get(k, '')
                        idea = ideas[i] if i < len(ideas) else ''
                        writer.writerow([domain_v, k, cl, idea, intent])

                    csv_data = sio.getvalue()
                    filename = fname.replace('.json', '.csv')
                    self.send_response(200)
                    self.send_header('Content-type', 'text/csv')
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                    self.end_headers()
                    self.wfile.write(csv_data.encode('utf-8'))
                    return
                except Exception as e:
                    self.send_error(500, str(e))
                    return
        elif path == '/api/domain':
            # GET: check if domain analysis result exists
            qs = urllib.parse.parse_qs(parsed.query)
            domain = qs.get('domain', [''])[0]
            if not domain:
                self.send_json_response({'ready': False})
                return
            fname = f"domain_keywords_{''.join([c if c.isalnum() else '_' for c in domain])}.json"
            fpath = OUTPUT_DIR / fname
            if fpath.exists():
                try:
                    with open(fpath, 'r', encoding='utf-8') as fp:
                        payload = json.load(fp)
                    self.send_json_response({'ready': True, 'payload': payload})
                except Exception:
                    self.send_json_response({'ready': False})
            else:
                # if a background task is running, indicate not ready
                running = domain in BACKGROUND_TASKS and BACKGROUND_TASKS[domain].is_alive()
                self.send_json_response({'ready': False, 'running': running})
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/run':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            keywords = data.get('keywords', '')
            
            # Run pipeline in background
            def run_bg():
                try:
                    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
                    cmd = ['python3', str(APP_DIR / 'seo_agent_tool.py'), '--keywords'] + kw_list
                    subprocess.run(cmd, cwd=str(APP_DIR))
                except Exception as e:
                    print(f"Error: {e}")
            
            thread = threading.Thread(target=run_bg)
            thread.daemon = True
            thread.start()
            
            self.send_json_response({'message': f'Pipeline started với {len(keywords.split(","))} keywords'})
        elif self.path == '/api/domain':
            # Start domain analysis in background
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
                domain = data.get('domain', '').strip()
            except Exception:
                domain = ''

            if not domain:
                self.send_json_response({'error': 'Missing domain parameter'})
                return

            # avoid duplicate runs
            if domain in BACKGROUND_TASKS and BACKGROUND_TASKS[domain].is_alive():
                self.send_json_response({'message': 'Domain analysis already running'})
                return

            def run_domain():
                try:
                    BACKGROUND_TASKS[domain] = threading.current_thread()
                    cmd = ['python3', str(APP_DIR / 'seo_agent_tool.py'), '--domain', domain]
                    subprocess.run(cmd, cwd=str(APP_DIR))
                except Exception as e:
                    print(f"Domain analysis error for {domain}: {e}")
                finally:
                    try:
                        del BACKGROUND_TASKS[domain]
                    except Exception:
                        pass

            t = threading.Thread(target=run_domain)
            t.daemon = True
            t.start()
            self.send_json_response({'message': f'Domain analysis started for {domain}'})
        else:
            self.send_error(404)
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def get_outlines_data(self):
        """Get outline files data"""
        files = []
        for f in sorted(OUTPUT_DIR.glob('outline_*.md')):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                size = f.stat().st_size / 1024
                files.append({
                    'name': f.name,
                    'size': f"{size:.1f}",
                    'content': content
                })
            except:
                pass
        return {'files': files}
    
    def get_research_data(self):
        """Get research files data"""
        files = []
        for f in sorted(OUTPUT_DIR.glob('research_*.json')):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    content = json.dumps(json.load(fp), indent=2)
                size = f.stat().st_size / 1024
                files.append({
                    'name': f.name,
                    'size': f"{size:.1f}",
                    'content': content
                })
            except:
                pass
        return {'files': files}
    
    def get_stats_data(self):
        """Get statistics"""
        outlines = list(OUTPUT_DIR.glob('outline_*.md'))
        research = list(OUTPUT_DIR.glob('research_*.json'))
        return {
            'outline_count': len(outlines),
            'research_count': len(research),
            'total_count': len(outlines) + len(research)
        }
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

# ====================================================================
# Main
# ====================================================================

def run_gui():
    """Run GUI server"""
    server = ReuseAddrHTTPServer(('0.0.0.0', PORT), SEOGUIHandler)
    
    print("\n" + "="*70)
    print("🚀 SEO Agent Pipeline — Web GUI")
    print("="*70)
    print(f"\n✅ Server running at: http://localhost:{PORT}")
    print(f"\n📝 Open in browser: http://localhost:{PORT}")
    print("\n💡 Ctrl+C để dừng server")
    print("\n" + "="*70 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
        server.shutdown()

if __name__ == '__main__':
    run_gui()

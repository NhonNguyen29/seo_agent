# SEO Agent Pipeline — GUI User Guide

## 🚀 Web Interface (Zero Dependencies)

**Status**: ✅ Running at `http://localhost:8000`

---

## 📖 How to Use

### 1. **Dashboard Tab** 📊
- View overview statistics
- See number of outlines and research files generated
- Quick start information

### 2. **Outlines Tab** 📄
- View all generated E-E-A-T outlines
- Click on any file to expand and read content
- Files show:
  - **File name** (keyword used)
  - **File size** (KB)
  - **Content preview** (click to expand)

### 3. **Research Tab** 🔍
- View SERP research data (JSON format)
- See competitor URLs and PAA questions
- Click to expand and view full research data

### 4. **Run Pipeline Tab** ▶️
- Enter keywords (comma-separated)
- Click "Chạy Pipeline" to generate new outlines
- Results appear within 10-30 seconds

---

## 🎯 Example Workflows

### Generate Single Outline
1. Go to "Run Pipeline" tab
2. Enter: `mobile SEO best practices`
3. Click "Chạy Pipeline"
4. Check "Outlines" tab for result

### Generate Multiple Outlines
1. Go to "Run Pipeline" tab
2. Enter: `mobile SEO, PWA optimization, Core Web Vitals`
3. Click "Chạy Pipeline"
4. All 3 outlines generate automatically

### View Competitor Analysis
1. Go to "Research" tab
2. Click any research file to expand
3. View:
   - URLs (competitor links)
   - Questions (People Also Ask)
   - Data structure: JSON

---

## 📊 Statistics Dashboard

The stats update automatically:
- **Outlines**: Total E-E-A-T outlines generated
- **Research**: Total SERP research files collected
- **Total Files**: Combined count

---

## 🔧 Technical Details

**Server**: Built-in Python HTTP server (no Flask needed)
**Port**: 8000
**URL**: http://localhost:8000

**Supported Operations**:
- ✅ View outlines (Markdown files)
- ✅ View research (JSON data)
- ✅ Run new pipelines
- ✅ Real-time statistics

**Features**:
- 🎨 Beautiful UI with gradients
- 📱 Responsive design (mobile-friendly)
- ⚡ Fast file loading
- 🔄 Auto-refresh stats

---

## 💡 Tips & Tricks

### Keyboard Shortcuts
- `Click file card` → Expand/collapse content
- `Tab key` → Navigate between tabs
- `Enter` → Submit form

### Performance
- Single keyword: ~5 seconds
- 3 keywords: ~15 seconds
- 10 keywords: ~50 seconds

### Best Practices
1. Use specific, long-tail keywords
2. Vietnam-focused keywords work best
3. Separate keywords with commas: `keyword1, keyword2`
4. Wait for pipeline to complete before running again

---

## 📍 File Locations

All output files stored in:
```
/home/saoviet2026/ZCode/seo_agent_pipeline_project/outputs/
```

**File Structure**:
```
outputs/
├── outline_*.md          (E-E-A-T outlines)
├── research_*.json       (SERP research data)
└── logs/                 (pipeline logs)
```

---

## 🆘 Troubleshooting

### "Server not starting"
```bash
cd /home/saoviet2026/ZCode/seo_agent_pipeline_project
python3 seo_gui.py
```

### "Port 8000 in use"
Change port in `seo_gui.py` line: `PORT = 8000` → `PORT = 8001`

### "No files showing"
Run pipeline first: Go to "Run Pipeline" tab and enter keywords

### "Page not loading"
Check terminal output for errors:
```bash
# Terminal should show:
# ✅ Server running at: http://localhost:8000
```

---

## 🎨 Interface Features

### Color Scheme
- **Primary**: Blue (#2563eb)
- **Success**: Green (#16a34a)
- **Background**: Purple gradient

### Responsive Design
- Desktop: Full layout
- Tablet: Adjusted spacing
- Mobile: Stacked layout

### Accessibility
- ARIA labels
- Keyboard navigation
- High contrast colors
- Fast load times

---

## 📚 Next Steps

1. **Use Demo Data**: Existing 5 outlines and research files
2. **Generate Custom**: Use "Run Pipeline" tab
3. **Batch Process**: Multiple keywords at once
4. **Export Results**: Download files from `outputs/` folder

---

## 🔗 API Endpoints (For Advanced Users)

### REST API
```
GET  /                    → Main interface
GET  /api/outlines       → List all outlines
GET  /api/research       → List all research
GET  /api/stats          → Statistics
POST /api/run            → Run pipeline with keywords
```

### Example POST Request
```bash
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"keywords": "mobile SEO, PWA"}'
```

---

**🎉 Enjoy the GUI! For any issues, check the terminal output.**

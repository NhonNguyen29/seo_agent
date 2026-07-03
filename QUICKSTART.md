# 🚀 SEO Agent Pipeline — QUICKSTART GUIDE

## Tổng Quan

**SEO Agent Pipeline** là một công cụ tự động hóa hoàn chỉnh để:
1. ✅ **Nghiên cứu từ khóa** trên Google Vietnam (mobile device)
2. ✅ **Cào nội dung** từ các trang ranking top
3. ✅ **Lọc trùng lặp** nội dung dựa trên ngữ nghĩa
4. ✅ **Sinh outline** bài viết chuẩn EEAT cho SEO hiện đại

---

## 📦 Cài Đặt Nhanh (2 phút)

### Bước 1: Clone/Tải Project
```bash
cd ~/ZCode/seo_agent_pipeline_project
```

### Bước 2: Cấu hình API Keys (tùy chọn)
```bash
cp config.example.env .env
```

Mở `.env` và thêm API keys (hoặc bỏ qua để dùng demo mode):
```env
SERPER_API_KEY=sk-xxxxx
FIRECRAWL_API_KEY=fc-xxxxx
OPENROUTER_API_KEY=sk-xxxxx
```

### Bước 3: Cài đặt Dependencies (tùy chọn)
Nếu bạn có pip installed:
```bash
pip3 install -r requirements.txt
```

Nếu không, công cụ sẽ chạy ở **demo mode** (fallback data) — tất cả đều hoạt động!

---

## ▶️ Chạy Pipeline

### 🎯 Demo Mode (Không cần API keys)
```bash
python3 seo_agent_tool.py --run-demo
```

**Kết quả**: 2 keywords được xử lý, output lưu ở `./outputs/`

### 📝 Với Keywords của Bạn
```bash
python3 seo_agent_tool.py --keywords "mobile SEO" "PWA optimization" "Core Web Vitals"
```

### 🎛️ Advanced Options
```bash
# Chạy riêng Step 1 (Research)
python3 seo_agent_tool.py --step research --keyword "mobile SEO"

# Chạy với log debug
python3 seo_agent_tool.py --keywords "SEO" --log-level DEBUG

# Lưu output vào thư mục tùy chỉnh
python3 seo_agent_tool.py --keywords "SEO" --out ./my_results
```

---

## 📂 Outputs Generated

Sau khi chạy, bạn sẽ có:

```
outputs/
├── research_keyword.json           # SERP data + PAA questions
├── outline_keyword.md              # Final article outline (EEAT format)
└── logs/
    └── pipeline.log                # Execution logs
```

### Sample Outline Structure
```markdown
# Outline: Mobile SEO Best Practices

## 1. Direct Answer (100 từ đầu)
- Định nghĩa cốt lõi
- Tại sao quan trọng

## 2. Khái niệm nền tảng
- Background
- Current context

## 3. How-to Guide
- Step 1
- Step 2
- Checklist

## 4. Real-world Examples
- Case study 1
- Case study 2

## 5. FAQ
- Q: ...? A: ...

## 6. Semantic Entities
- Entity list cần có
```

---

## 🔑 API Keys (Where to Get Them)

| Service | Link | Cost | Required |
|---------|------|------|----------|
| **Serper.dev** | https://serper.dev | $0.01/query | For real SERP data |
| **Firecrawl** | https://www.firecrawl.dev | $0.05/page | For web scraping |
| **OpenRouter** | https://openrouter.ai | ~$0.01-0.1 | For LLM outlines |

**Demo Mode**: Run without any keys — all fallback data works!

---

## ⚡ Performance Benchmarks

| Task | Time | Notes |
|------|------|-------|
| 1 keyword full pipeline | ~5s (demo) | With fallback data |
| + with real APIs | 30-60s | Depends on SERP/scrape speed |
| 10 keywords batch | ~1-2 min | With real APIs |

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Install deps: `pip3 install requests` (core libs only needed) |
| API key errors | Expected in demo mode; run with `--run-demo` |
| Slow scraping | Add `--step research` to test individual steps |
| Outline looks generic | Add real API keys for LLM-powered outlines |

---

## 📖 Full Documentation

See `README.md` for:
- Complete architecture
- All configuration options
- Advanced customization
- Integration examples

---

## 💡 Next Steps

1. **Run demo** to understand the flow
2. **Get API keys** from services above
3. **Set up `.env`** with your keys
4. **Run with real keywords**: `python3 seo_agent_tool.py --keywords "your keyword"`
5. **Refine outlines** in your favorite editor
6. **Pass to copywriter** for full article writing

---

## 📧 Support

For issues or questions:
1. Check `README.md` Troubleshooting section
2. Review individual `pipeline_0X_*.md` specs
3. Run with `--log-level DEBUG` for detailed logs

---

**Version**: 1.0  
**Last Updated**: 2026-07-03  
**Status**: ✅ Ready for Production Use (with real APIs)

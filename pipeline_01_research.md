# Pipeline 1: Mobile Research Agent Skill

## 1. Mục tiêu (Objective)
Tự động nghiên cứu thị trường, thu thập dữ liệu thứ hạng tìm kiếm giả lập môi trường di động thực tế tại Việt Nam dựa trên chủ đề hoặc tên miền (domain) đầu vào.

## 2. Bản chất kỹ thuật SEO (SEO Core Concept)
- **Mobile-First Indexing**: Google ưu tiên tối đa dữ liệu hiển thị trên thiết bị di động.
- **Search Intent Catching**: Thu thập ý định tìm kiếm thực tế của người dùng thông qua kết quả xếp hạng và hộp câu hỏi gợi ý.

## 3. Công nghệ tích hợp (Tech Stack)
- **Ngôn ngữ**: Python
- **API chính**: Serper.dev API (hoặc ValueSerp API)

## 4. Tham số cấu hình API bắt buộc (Payload Configuration)
```json
{
  "gl": "vn",
  "hl": "vi",
  "device": "mobile"
}
```

## 5. Luồng xử lý dữ liệu (Workflow & Output)
1. **Input**: Nhận chuỗi ký tự `Domain` hoặc `Topic / Keyword` từ người dùng.
2. **Execution**: Gửi yêu cầu HTTP POST đến endpoint của Serper API kèm theo bộ tham số cấu hình di động.
3. **Output**: Trả về một file JSON hoặc Dictionary chứa:
   - Danh sách **Top 10 URL** đang dẫn đầu bảng xếp hạng.
   - Danh sách các câu hỏi trong hộp dữ liệu **"People Also Asked" (Mọi người cũng hỏi)**.

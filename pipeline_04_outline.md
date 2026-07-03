# Pipeline 4: Mass Outline Generator Skill

## 1. Mục tiêu (Objective)
Tự động tạo ra hàng loạt cấu trúc khung bài viết (Outline) chuẩn cấu trúc SEO ngữ nghĩa tiên tiến nhất dựa trên các khoảng trống nội dung đã lọc.

## 2. Bản chất kỹ thuật SEO (SEO Core Concept)
- **E-E-A-T Framework**: Đáp ứng bộ tiêu chuẩn Kinh nghiệm (Experience), Chuyên môn (Expertise), Thẩm quyền (Authoritativeness), Tin cậy (Trustworthiness).
- **Semantic SEO**: Bao phủ toàn bộ các thực thể (Entities) liên quan đến chủ đề để Google hiểu sâu ngữ cảnh.

## 3. Công nghệ tích hợp (Tech Stack)
- **Cổng kết nối**: OpenRouter API.
- **Mô hình suy luận cấu trúc (Reasoning Layer)**: DeepSeek-R1 hoặc OpenAI o1-mini.
- **Mô hình địa phương hóa văn phong (Localization Layer)**: Anthropic Claude 3.5 Sonnet hoặc Google Gemini 1.5 Pro (cho ngôn ngữ Tiếng Việt tự nhiên).

## 4. Quy tắc Prompting bắt buộc cho AI (Hard Prompt Rules)
Mỗi Outline sinh ra phải tuân thủ nghiêm ngặt cấu trúc sau:
1. **Direct Answer (100 từ đầu tiên)**: Phải trả lời trực diện câu hỏi/Search Intent cốt lõi của người dùng để tối ưu Helpful Content.
2. **Heading Hierarchy**: Phân cấp thẻ tiêu đề H2, H3, H4 logic, rõ ràng. Nghiêm cấm nhồi nhét từ khóa thô thiển vào tiêu đề.
3. **Semantic Entities**: Tự động liệt kê ít nhất 5-7 thực thể dữ liệu liên quan cần phải có trong bài viết để bổ trợ ngữ cảnh.

## 5. Luồng xử lý dữ liệu (Workflow & Output)
1. **Input**: Bộ dữ liệu từ khóa độc nhất thu được từ Pipeline 3.
2. **Execution**: Gửi Prompt cấu trúc qua OpenRouter -> Xử lý chuỗi suy luận bằng DeepSeek-R1 -> Chuẩn hóa văn phong bằng Claude 3.5 Sonnet.
3. **Output**: File Outline SEO hoàn chỉnh ở định dạng Markdown, sẵn sàng chuyển qua khâu viết bài chi tiết.

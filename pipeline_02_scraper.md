# Pipeline 2: Content Scraper Agent Skill

## 1. Mục tiêu (Objective)
Tự động truy cập vào danh sách các URL đối thủ cạnh tranh từ Pipeline 1, cào và bóc tách lấy nội dung cốt lõi của bài viết mà không bị chặn.

## 2. Bản chất kỹ thuật SEO (SEO Core Concept)
- **Anti-Scraping Bypass**: Vượt qua các hệ thống tường lửa (Cloudflare) và xử lý các website render bằng Javascript.
- **Content Cleaning**: Loại bỏ nhiễu dữ liệu (Menu, Banner quảng cáo, Widget, Footer) để AI chỉ phân tích văn bản bài viết thuần túy.

## 3. Công nghệ tích hợp (Tech Stack)
- **Ngôn ngữ**: Python
- **Thư viện/API**: Firecrawl API (Ưu tiên) hoặc Jina Reader API. Không dùng BeautifulSoup truyền thống.

## 4. Đặc tả định dạng dữ liệu (Data Format Specification)
- Toàn bộ dữ liệu HTML thô sau khi quét phải được chuyển đổi tự động sang cấu trúc **Markdown sạch (.md)**.
- Giữ nguyên các thẻ định dạng tiêu đề cơ bản `#`, `##`, `###` của bài viết gốc để phục vụ phân tích cấu trúc.

## 5. Luồng xử lý dữ liệu (Workflow & Output)
1. **Input**: Danh sách Top 10 URL từ kết quả đầu ra của Pipeline 1.
2. **Execution**: Gọi API Firecrawl để xử lý đồng thời (Concurrent Processing) các URL.
3. **Output**: Bộ dữ liệu chứa nội dung văn bản dạng Markdown của toàn bộ các trang đối thủ.

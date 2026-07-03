# Pipeline 3: Semantic & Duplicate Filter Skill

## 1. Mục tiêu (Objective)
Phân tích ngữ nghĩa toàn bộ nội dung đã cào từ đối thủ so với kho dữ liệu hiện tại của hệ thống nhằm tìm ra khoảng trống nội dung (Content Gap) và loại bỏ trùng lặp văn bản.

## 2. Bản chất kỹ thuật SEO (SEO Core Concept)
- **Google Helpful Content System**: Google phạt nặng các nội dung sao chép, xào xáo hoặc dịch thô không mang lại giá trị độc nhất.
- **Unique Value Discovery**: Tìm kiếm các góc độ nội dung mới mà đối thủ chưa khai thác tốt.

## 3. Công nghệ tích hợp (Tech Stack)
- **Embedding Model**: OpenAI `text-embedding-3-small` API (hoặc Cohere Embed).
- **Vector Database**: Qdrant / Pinecone / Milvus.
- **Thuật toán**: Hệ số tương đồng Cosine (Cosine Similarity).

## 4. Ngưỡng logic loại bỏ (Business Logic Threshold)
- Tính toán khoảng cách Vector giữa bài viết dự kiến và bài viết đối thủ.
- **Nếu Cosine Similarity > 0.75 (75%)**: Xác định là nội dung trùng lặp ngữ nghĩa cao. 
- **Action**: Agent tự động từ chối hướng tiếp cận cũ, ép buộc thay đổi góc nhìn hoặc bổ sung thêm thông tin chuyên sâu.

## 5. Luồng xử lý dữ liệu (Workflow & Output)
1. **Input**: Văn bản Markdown thô từ Pipeline 2.
2. **Execution**: Chuyển đổi văn bản thành Vector nhúng -> Đẩy vào Vector DB -> Truy vấn đo độ trùng lặp.
3. **Output**: Danh sách các chủ đề/từ khóa đã được làm sạch, đảm bảo 100% tính độc nhất (Unique Content).

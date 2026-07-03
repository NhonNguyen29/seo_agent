# Pipeline 3: Semantic & Duplicate Filter Skill

## 1. Mục tiêu
Phân tích ngữ nghĩa trên văn bản đã cào để tìm "content gaps" và loại bỏ nội dung trùng lặp về ý (semantic duplicates), đảm bảo kết quả đầu ra có giá trị độc đáo.

## 2. Thay đổi chính
- Loại bỏ `spaCy` hoàn toàn khỏi pipeline.
- Chuyển sang `sentence-transformers` (embedder local) làm engine chính để tính tương đồng ngữ nghĩa.
- Mặc định sử dụng mô hình nhúng: `all-MiniLM-L6-v2`.

## 3. Tech stack cập nhật
- **Embedder (local)**: `sentence-transformers` (`all-MiniLM-L6-v2`).
- **Vector DB (tuỳ chọn)**: Qdrant / Pinecone / Milvus. Hệ thống cũng có thể tính cosine trực tiếp trên vectors in-memory cho demo.
- **Thuật toán**: Cosine similarity giữa vector embeddings.

## 4. Ngưỡng logic (Business Rules)
- Nếu cosine similarity giữa bài tham chiếu và nội dung đối thủ > `SEMANTIC_SIMILARITY_THRESHOLD` (mặc định 0.75) => coi là trùng ngữ nghĩa và loại bỏ.
- Ngưỡng này có thể tùy chỉnh trong `config` / `.env`.

## 5. Luồng xử lý (Workflow)
1. Nhận danh sách văn bản Markdown từ Pipeline 2.
2. Chia nhỏ/tối giản văn bản nếu quá dài (token cap), rồi encode bằng `sentence-transformers` thành vectors.
3. Tính cosine similarity giữa vector của topic/keyword reference và từng document.
4. Lưu lại những document có similarity thấp hơn ngưỡng (unique points) để phục vụ Outline Generator.

## 6. Cài đặt & chạy
- Cập nhật dependencies (đã loại `spacy`):

```bash
cd seo_agent_pipeline_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Chạy demo pipeline:

```bash
.venv/bin/python seo_agent_tool.py --run-demo
```

## 7. Ghi chú
- `sentence-transformers` hoạt động offline (tải weights lần đầu), phù hợp với môi trường không muốn phụ thuộc API trả phí.
- Nếu `sentence-transformers` không khả dụng, pipeline tự động fallback về so sánh token-based (Jaccard) như biện pháp tạm thời.
- Tùy chọn nâng cao: kết nối vector DB để lưu history embeddings và truy vấn nhanh cho volume lớn.

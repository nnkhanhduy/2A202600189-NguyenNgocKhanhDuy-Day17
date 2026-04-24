# Multi-Memory Agent (Lab #17)

Dự án này là bài nộp cho **Lab #17: Build Multi-Memory Agent với LangGraph**. 
Agent được thiết kế với kiến trúc bộ nhớ đa tầng (4 lớp) để cung cấp khả năng cá nhân hóa sâu sắc, ghi nhớ ngữ cảnh lâu dài và có thể tra cứu kiến thức bên ngoài một cách linh hoạt.

## 🧠 Kiến trúc Bộ nhớ (Full Memory Stack)

Hệ thống tích hợp 4 loại bộ nhớ hoạt động song song thông qua **LangGraph**:

1. **Short-term Memory (Chat History):** 
   - Quản lý ngữ cảnh cuộc trò chuyện gần nhất.
   - Sử dụng cơ chế Sliding Window với thư viện `tiktoken` để tự động cắt tỉa (trim) khi vượt quá 4000 tokens, ngăn chặn lỗi context overflow.
2. **Long-term Profile:**
   - Trích xuất và lưu trữ các "sự thật" về người dùng (Tên, tuổi, sở thích, dị ứng...) vào file `profile.json`.
   - Có cơ chế xử lý xung đột (Conflict Handling): tự động ghi đè thông tin cũ nếu người dùng thay đổi ý định (vd: đổi từ dị ứng sữa sang đậu nành).
3. **Episodic Memory:**
   - Ghi nhận và tóm tắt lại các sự kiện hoặc quyết định quan trọng của người dùng sau mỗi lượt chat vào file `episodes.json`.
4. **Semantic Memory:**
   - Sử dụng Vector Database (**ChromaDB** in-memory) kết hợp với OpenAI Embeddings (`text-embedding-3-small`).
   - Có khả năng tra cứu các kiến thức mẫu (FAQs) hoặc tài liệu hướng dẫn kỹ thuật để cung cấp câu trả lời chính xác dựa trên ngữ cảnh.

## 🚀 Cài đặt và Chạy

### 1. Cài đặt thư viện
Yêu cầu Python 3.9 trở lên.
```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường
Tạo file `.env` từ file `.env.example` và điền OpenAI API Key của bạn vào:
```env
OPENAI_API_KEY="sk-xxxx..."
```

### 3. Trải nghiệm Giao diện UI (Streamlit)
Dự án đi kèm một giao diện Web trực quan để tương tác với Agent và theo dõi trạng thái của các tầng bộ nhớ theo thời gian thực:
```bash
streamlit run app.py
```

### 4. Chạy Benchmark
Để tự động chạy kịch bản kiểm thử (10 multi-turn scenarios) so sánh hiệu năng giữa việc có bộ nhớ và không có bộ nhớ:
```bash
python run_benchmark.py
```
Kết quả chi tiết sẽ được tự động ghi đè vào file `BENCHMARK.md`.

## 📁 Cấu trúc thư mục

- `agent_graph.py`: Chứa logic cốt lõi của LangGraph (State, Router, Prompts, Update node).
- `memory_backends.py`: Triển khai 4 loại memory backend.
- `app.py`: Giao diện chat Streamlit.
- `run_benchmark.py`: Script tự động đánh giá (Auto-evaluation).
- `BENCHMARK.md`: Báo cáo kết quả benchmark và phần Reflection về Privacy/Limitations.
- `profile.json` & `episodes.json`: Các file dữ liệu tự sinh ra khi agent ghi nhớ.

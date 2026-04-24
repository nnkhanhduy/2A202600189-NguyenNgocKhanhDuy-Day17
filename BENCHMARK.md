# BENCHMARK REPORT

## 1. Kết quả chạy 10 Multi-turn Conversations

| # | Scenario | No-memory result (Pass/Fail) | With-memory result (Pass/Fail) | With-memory Answer Snippet |
|---|---|---|---|---|
| 1 | Recall user name after 6 turns | Fail | **Pass** | Có chứ, bạn tên là Linh! Nếu bạn cần gì thêm, hãy ... |
| 2 | Allergy conflict update | Pass | **Pass** | Bạn bị dị ứng với đậu nành. Nếu bạn cần thêm thông... |
| 3 | Recall previous debug lesson (Episodic/Semantic) | Pass | **Pass** | Đúng rồi, bạn đã từng hỏi về lỗi 'port is already ... |
| 4 | Retrieve FAQ chunk - Refund | Fail | **Pass** | Thời hạn cụ thể để yêu cầu hoàn tiền là 30 ngày kể... |
| 5 | Retrieve FAQ chunk - Password | Fail | **Pass** | Bạn cần vào mục **Cài đặt** (Settings) trên thiết ... |
| 6 | Episodic - Decision making | Fail | **Pass** | Bạn đã quyết định chọn gói Pro vì nó nhiều tính nă... |
| 7 | Hobby update & recall | Pass | **Pass** | Dựa trên sở thích đọc sách của bạn, có một số hoạt... |
| 8 | Multiple facts update | Fail | **Pass** | Có, bạn 25 tuổi và sống ở Đà Nẵng. Nếu bạn cần thô... |
| 9 | Job conflict update | Fail | **Pass** | Nghề nghiệp hiện tại của bạn là Developer. Nếu bạn... |
| 10 | Trim/token budget test | Fail | **Pass** | Màu yêu thích của bạn là màu xanh lá! |

## 2. Reflection privacy/limitations

### 2.1. Memory nào giúp agent nhất?
- **Long-term Profile & Semantic Memory**: Giúp cá nhân hóa cao (nhớ tên, sở thích, dị ứng) và cung cấp kiến thức thực tế (FAQ, chính sách) mà mô hình gốc không biết.

### 2.2. Memory nào rủi ro nhất nếu retrieve sai?
- **Semantic Memory (ChromaDB)**: Rủi ro nhất khi retrieve sai tài liệu hướng dẫn (ví dụ: tư vấn sai chính sách hoàn tiền có thể gây thiệt hại cho doanh nghiệp).
- **Long-term Profile**: Cực kỳ rủi ro nếu hệ thống chia sẻ nhầm profile của User A sang cho User B (lộ PII như địa chỉ, dị ứng, thông tin cá nhân).

### 2.3. Quản lý PII, Consent, và Deletion
- Khi lưu PII (Thông tin định danh cá nhân) vào Profile hoặc Episodic, hệ thống cần cơ chế mã hóa hoặc Consent rõ ràng từ người dùng.
- Nếu User yêu cầu xóa memory (Right to be Forgotten), ta phải xóa ở **cả 4 backends**: Xóa lịch sử (Short-term), Xóa tệp JSON profile/episodic, và xóa các vectors cá nhân khỏi DB nếu có.

### 2.4. Limitation kỹ thuật của kiến trúc hiện tại
- Việc sử dụng Prompt Injection (nhét toàn bộ profile, episodic vào prompt) không scale được nếu profile của người dùng quá lớn. Dễ bị vượt token limit của LLM.
- Token Trim ở Short-term đang dùng word-count x 1.3, không hoàn toàn chính xác như dùng thư viện tiktoken.
- LLM extraction tốn chi phí và có độ trễ cao (phải gọi thêm 1 API call với Structured Output sau mỗi lượt hội thoại để cập nhật memory).

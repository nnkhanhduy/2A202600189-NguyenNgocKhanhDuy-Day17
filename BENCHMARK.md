# 📊 BÁO CÁO ĐÁNH GIÁ AGENT (BENCHMARK REPORT)

## 1. Tóm tắt kết quả (Executive Summary)

- **Phiên bản Agent:** Multi-Memory LangGraph Agent (4 layers)
- **Tổng số kịch bản test:** 10
- **Tỉ lệ thành công (Không bộ nhớ):** 3/10 (30%)
- **Tỉ lệ thành công (Có bộ nhớ):** 10/10 (100%)
- **Hiệu quả cải thiện:** +70% thành công nhờ hệ thống bộ nhớ đa tầng.

## 2. Chi tiết kết quả 10 Multi-turn Conversations

| ID | Kịch bản kiểm thử | Nhóm Memory chính | No-memory | With-memory | Kết quả chi tiết (With-memory) |
|---|---|---|---|---|---|
| 1 | Recall user name after 6 turns | Profile/Short-term | Fail | **Pass** | Có chứ! Bạn tên là Linh. Nếu bạn cần thêm thông tin gì, hãy cho tôi biết nhé! |
| 2 | Allergy conflict update | Profile (Conflict) | Pass | **Pass** | Bạn bị dị ứng với đậu nành. Nếu bạn cần thông tin hoặc gợi ý về thực phẩm an toàn, hãy cho tôi biết ... |
| 3 | Recall previous debug lesson (Episodic/Semantic) | Episodic/Semantic | Pass | **Pass** | Đúng rồi, bạn đã từng hỏi về lỗi 'port is already allocated' khi chạy Docker. Nếu bạn cần thêm thông... |
| 4 | Retrieve FAQ chunk - Refund | Semantic (FAQ) | Fail | **Pass** | Thời hạn cụ thể để yêu cầu hoàn tiền là 30 ngày kể từ ngày mua hàng. |
| 5 | Retrieve FAQ chunk - Password | Semantic (FAQ) | Fail | **Pass** | Bạn cần vào mục **Cài đặt** (Settings) trên thiết bị hoặc ứng dụng của bạn. Sau đó, tìm và chọn mục ... |
| 6 | Episodic - Decision making | Episodic (Decision) | Fail | **Pass** | Bạn đã quyết định chọn gói Pro vì nó nhiều tính năng hơn. Nếu bạn cần thêm thông tin hoặc hỗ trợ gì ... |
| 7 | Hobby update & recall | Profile/Episodic | Pass | **Pass** | Dựa trên sở thích đọc sách của bạn, có một số hoạt động thú vị bạn có thể làm vào cuối tuần:  1. **Đ... |
| 8 | Multiple facts update | Profile (Multi-fact) | Fail | **Pass** | Có, bạn 25 tuổi và sống ở Đà Nẵng. Nếu bạn cần thông tin hay hỗ trợ gì thêm, hãy cho tôi biết nhé! |
| 9 | Job conflict update | Profile (Conflict) | Fail | **Pass** | Nghề nghiệp hiện tại của bạn là Developer. Nếu bạn cần thông tin hoặc hỗ trợ liên quan đến công việc... |
| 10 | Trim/token budget test | Short-term (Budget) | Fail | **Pass** | Màu yêu thích của bạn là màu xanh lá! |

## 3. Phân tích và Reflection (Theo Rubric)

### 3.1. Phân tích vai trò các tầng bộ nhớ
- **Long-term Profile**: Giúp Agent cá nhân hóa cuộc hội thoại (Case #1, #8). Cơ chế ghi đè Fact giúp xử lý mâu thuẫn thông tin (Case #2, #9).
- **Episodic Memory**: Ghi lại các quyết định quan trọng (Case #6) giúp Agent không hỏi lại những gì đã thống nhất.
- **Semantic Memory**: Cung cấp kiến thức chuyên biệt (Case #4, #5) mà model GPT không được train sẵn (vd: chính sách công ty cụ thể).
- **Short-term Memory**: Duy trì mạch hội thoại và tự động cắt tỉa (Trim) để tối ưu chi phí và tránh lỗi tràn context (Case #10).

### 3.2. Quyền riêng tư (Privacy) & Quản lý PII
- **Rủi ro**: Các thông tin như địa chỉ, dị ứng, nghề nghiệp (PII) được lưu dưới dạng văn bản thuần trong JSON. Nếu hệ thống bị xâm nhập, dữ liệu này rất nhạy cảm.
- **Giải pháp**: Cần cơ chế mã hóa dữ liệu khi lưu (At-rest encryption) và xóa dữ liệu định kỳ (TTL). Khi người dùng yêu cầu 'Quên tôi đi', hệ thống phải xóa sạch cả file JSON và Vector DB.

### 3.3. Giới hạn kỹ thuật (Limitations)
- Hệ thống hiện tại dùng 'Prompt Injection' để nhồi bộ nhớ vào ngữ cảnh. Nếu Profile quá lớn, chi phí Token sẽ tăng rất nhanh.
- Token Trim ở Short-term đang dùng thư viện tiktoken chuẩn xác.
- LLM extraction tốn chi phí và có độ trễ cao (phải gọi thêm 1 API call với Structured Output sau mỗi lượt hội thoại để cập nhật memory).

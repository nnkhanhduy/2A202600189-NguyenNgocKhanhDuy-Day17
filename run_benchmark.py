import json
from agent_graph import MultiMemoryAgent
import time

scenarios = [
    {
        "id": 1,
        "name": "Recall user name after 6 turns",
        "turns": [
            "Chào bạn, tôi tên là Linh.",
            "Tôi muốn hỏi thời tiết hôm nay thế nào?",
            "À, tôi định đi chơi.",
            "Bạn có gợi ý địa điểm nào ở Hà Nội không?",
            "Tôi thích mấy chỗ yên tĩnh.",
            "Cảm ơn bạn đã gợi ý.",
            "Bạn có nhớ tôi tên là gì không?"
        ],
        "expected": "Linh"
    },
    {
        "id": 2,
        "name": "Allergy conflict update",
        "turns": [
            "Tôi bị dị ứng sữa bò nhé.",
            "Bạn nhớ thông tin này để gọi món cho tôi nha.",
            "À nhầm, tôi dị ứng đậu nành chứ không phải sữa bò.",
            "Tóm lại, tôi bị dị ứng với cái gì?"
        ],
        "expected": "đậu nành"
    },
    {
        "id": 3,
        "name": "Recall previous debug lesson (Episodic/Semantic)",
        "turns": [
            "Lỗi 'port is already allocated' khi chạy docker thì làm sao?",
            "Cảm ơn, vậy bạn nhớ là tôi đã từng hỏi về lỗi docker này đúng không?"
        ],
        "expected": "docker"
    },
    {
        "id": 4,
        "name": "Retrieve FAQ chunk - Refund",
        "turns": [
            "Tôi muốn hỏi về chính sách hoàn tiền của công ty.",
            "Thời hạn cụ thể là bao nhiêu ngày?"
        ],
        "expected": "30 ngày"
    },
    {
        "id": 5,
        "name": "Retrieve FAQ chunk - Password",
        "turns": [
            "Làm sao để đổi mật khẩu?",
            "Tôi phải vào mục nào?"
        ],
        "expected": "Settings"
    },
    {
        "id": 6,
        "name": "Episodic - Decision making",
        "turns": [
            "Tôi đang phân vân giữa gói Basic và gói Pro.",
            "Tôi nghĩ tôi sẽ chọn gói Pro vì nó nhiều tính năng hơn.",
            "Chốt lại, tôi vừa quyết định chọn gói nào?"
        ],
        "expected": "Pro"
    },
    {
        "id": 7,
        "name": "Hobby update & recall",
        "turns": [
            "Sở thích của tôi là đọc sách.",
            "Cuối tuần tôi hay ở nhà.",
            "Theo bạn cuối tuần tôi có thể làm gì dựa trên sở thích?"
        ],
        "expected": "đọc sách"
    },
    {
        "id": 8,
        "name": "Multiple facts update",
        "turns": [
            "Tôi 25 tuổi và sống ở Đà Nẵng.",
            "Bạn có biết tôi bao nhiêu tuổi và ở đâu không?"
        ],
        "expected": "25 tuổi"
    },
    {
        "id": 9,
        "name": "Job conflict update",
        "turns": [
            "Tôi hiện đang là sinh viên.",
            "À thực ra tôi vừa tốt nghiệp và giờ là một Developer.",
            "Nghề nghiệp hiện tại của tôi là gì?"
        ],
        "expected": "Developer"
    },
    {
        "id": 10,
        "name": "Trim/token budget test",
        "turns": [
            "Tôi rất thích màu xanh lá.",
            "Hôm nay trời đẹp quá.",
            "Bạn có biết nấu ăn không?",
            "Tôi thì chỉ biết luộc trứng.",
            "Thật ra tôi cũng ít khi vào bếp.",
            "Bạn thích con vật nào?",
            "Tôi hỏi lại một chút, màu yêu thích của tôi là màu gì?"
        ],
        "expected": "xanh lá"
    }
]

def run_scenarios(enable_memory: bool):
    agent = MultiMemoryAgent()
    results = []
    
    for s in scenarios:
        agent.reset_all()
        # Sleep a bit to avoid rate limits if any
        time.sleep(1)
        
        final_answer = ""
        for i, turn in enumerate(s["turns"]):
            final_answer = agent.invoke(turn, enable_memory=enable_memory)
            
        pass_test = "Pass" if s["expected"].lower() in final_answer.lower() else "Fail"
        
        results.append({
            "id": s["id"],
            "name": s["name"],
            "answer": final_answer.replace('\n', ' '),
            "pass": pass_test
        })
        
    return results

def generate_report():
    print("Running without memory...")
    no_mem_results = run_scenarios(enable_memory=False)
    
    print("Running with memory...")
    mem_results = run_scenarios(enable_memory=True)
    
    # Generate Markdown
    md_content = "# BENCHMARK REPORT\n\n"
    md_content += "## 1. Kết quả chạy 10 Multi-turn Conversations\n\n"
    md_content += "| # | Scenario | No-memory result (Pass/Fail) | With-memory result (Pass/Fail) | With-memory Answer Snippet |\n"
    md_content += "|---|---|---|---|---|\n"
    
    for i in range(len(scenarios)):
        no_mem = no_mem_results[i]
        mem = mem_results[i]
        ans_snippet = mem['answer'][:50] + "..." if len(mem['answer']) > 50 else mem['answer']
        
        md_content += f"| {i+1} | {mem['name']} | {no_mem['pass']} | **{mem['pass']}** | {ans_snippet} |\n"
        
    md_content += "\n## 2. Reflection privacy/limitations\n\n"
    md_content += "### 2.1. Memory nào giúp agent nhất?\n"
    md_content += "- **Long-term Profile & Semantic Memory**: Giúp cá nhân hóa cao (nhớ tên, sở thích, dị ứng) và cung cấp kiến thức thực tế (FAQ, chính sách) mà mô hình gốc không biết.\n\n"
    
    md_content += "### 2.2. Memory nào rủi ro nhất nếu retrieve sai?\n"
    md_content += "- **Semantic Memory (ChromaDB)**: Rủi ro nhất khi retrieve sai tài liệu hướng dẫn (ví dụ: tư vấn sai chính sách hoàn tiền có thể gây thiệt hại cho doanh nghiệp).\n"
    md_content += "- **Long-term Profile**: Cực kỳ rủi ro nếu hệ thống chia sẻ nhầm profile của User A sang cho User B (lộ PII như địa chỉ, dị ứng, thông tin cá nhân).\n\n"
    
    md_content += "### 2.3. Quản lý PII, Consent, và Deletion\n"
    md_content += "- Khi lưu PII (Thông tin định danh cá nhân) vào Profile hoặc Episodic, hệ thống cần cơ chế mã hóa hoặc Consent rõ ràng từ người dùng.\n"
    md_content += "- Nếu User yêu cầu xóa memory (Right to be Forgotten), ta phải xóa ở **cả 4 backends**: Xóa lịch sử (Short-term), Xóa tệp JSON profile/episodic, và xóa các vectors cá nhân khỏi DB nếu có.\n\n"
    
    md_content += "### 2.4. Limitation kỹ thuật của kiến trúc hiện tại\n"
    md_content += "- Việc sử dụng Prompt Injection (nhét toàn bộ profile, episodic vào prompt) không scale được nếu profile của người dùng quá lớn. Dễ bị vượt token limit của LLM.\n"
    md_content += "- Token Trim ở Short-term đang dùng word-count x 1.3, không hoàn toàn chính xác như dùng thư viện tiktoken.\n"
    md_content += "- LLM extraction tốn chi phí và có độ trễ cao (phải gọi thêm 1 API call với Structured Output sau mỗi lượt hội thoại để cập nhật memory).\n"

    with open("BENCHMARK.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print("BENCHMARK.md generated successfully.")

if __name__ == "__main__":
    generate_report()

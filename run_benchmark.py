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
    
    no_mem_pass = sum(1 for x in no_mem_results if x["pass"] == "Pass")
    with_mem_pass = sum(1 for x in mem_results if x["pass"] == "Pass")

    # Generate Markdown
    md_content = "# 📊 BÁO CÁO ĐÁNH GIÁ AGENT (BENCHMARK REPORT)\n\n"
    
    md_content += "## 1. Tóm tắt kết quả (Executive Summary)\n\n"
    md_content += f"- **Phiên bản Agent:** Multi-Memory LangGraph Agent (4 layers)\n"
    md_content += f"- **Tổng số kịch bản test:** {len(scenarios)}\n"
    md_content += f"- **Tỉ lệ thành công (Không bộ nhớ):** {no_mem_pass}/{len(scenarios)} ({no_mem_pass*10}%)\n"
    md_content += f"- **Tỉ lệ thành công (Có bộ nhớ):** {with_mem_pass}/{len(scenarios)} ({with_mem_pass*10}%)\n"
    md_content += f"- **Hiệu quả cải thiện:** +{(with_mem_pass - no_mem_pass)*10}% thành công nhờ hệ thống bộ nhớ đa tầng.\n\n"
    md_content += "## 2. Chi tiết kết quả 10 Multi-turn Conversations\n\n"
    md_content += "| ID | Kịch bản kiểm thử | Nhóm Memory chính | No-memory | With-memory | Kết quả chi tiết (With-memory) |\n"
    md_content += "|---|---|---|---|---|---|\n"
    
    memory_mapping = {
        1: "Profile/Short-term",
        2: "Profile (Conflict)",
        3: "Episodic/Semantic",
        4: "Semantic (FAQ)",
        5: "Semantic (FAQ)",
        6: "Episodic (Decision)",
        7: "Profile/Episodic",
        8: "Profile (Multi-fact)",
        9: "Profile (Conflict)",
        10: "Short-term (Budget)"
    }

    for i in range(len(scenarios)):
        no_mem = no_mem_results[i]
        mem = mem_results[i]
        category = memory_mapping.get(i+1, "General")
        ans_snippet = mem['answer'][:100] + "..." if len(mem['answer']) > 100 else mem['answer']
        
        no_label = "Fail" if no_mem['pass'] == "Fail" else "Pass"
        mem_label = "Fail" if mem['pass'] == "Fail" else "Pass"
        
        md_content += f"| {i+1} | {mem['name']} | {category} | {no_label} | **{mem_label}** | {ans_snippet} |\n"
        
    md_content += "\n## 3. Phân tích và Reflection (Theo Rubric)\n\n"
    
    md_content += "### 3.1. Phân tích vai trò các tầng bộ nhớ\n"
    md_content += "- **Long-term Profile**: Giúp Agent cá nhân hóa cuộc hội thoại (Case #1, #8). Cơ chế ghi đè Fact giúp xử lý mâu thuẫn thông tin (Case #2, #9).\n"
    md_content += "- **Episodic Memory**: Ghi lại các quyết định quan trọng (Case #6) giúp Agent không hỏi lại những gì đã thống nhất.\n"
    md_content += "- **Semantic Memory**: Cung cấp kiến thức chuyên biệt (Case #4, #5) mà model GPT không được train sẵn (vd: chính sách công ty cụ thể).\n"
    md_content += "- **Short-term Memory**: Duy trì mạch hội thoại và tự động cắt tỉa (Trim) để tối ưu chi phí và tránh lỗi tràn context (Case #10).\n\n"
    
    md_content += "### 3.2. Quyền riêng tư (Privacy) & Quản lý PII\n"
    md_content += "- **Rủi ro**: Các thông tin như địa chỉ, dị ứng, nghề nghiệp (PII) được lưu dưới dạng văn bản thuần trong JSON. Nếu hệ thống bị xâm nhập, dữ liệu này rất nhạy cảm.\n"
    md_content += "- **Giải pháp**: Cần cơ chế mã hóa dữ liệu khi lưu (At-rest encryption) và xóa dữ liệu định kỳ (TTL). Khi người dùng yêu cầu 'Quên tôi đi', hệ thống phải xóa sạch cả file JSON và Vector DB.\n\n"
    
    md_content += "### 3.3. Giới hạn kỹ thuật (Limitations)\n"
    md_content += "- Hệ thống hiện tại dùng 'Prompt Injection' để nhồi bộ nhớ vào ngữ cảnh. Nếu Profile quá lớn, chi phí Token sẽ tăng rất nhanh.\n"
    md_content += "- Token Trim ở Short-term đang dùng thư viện tiktoken chuẩn xác.\n"
    md_content += "- LLM extraction tốn chi phí và có độ trễ cao (phải gọi thêm 1 API call với Structured Output sau mỗi lượt hội thoại để cập nhật memory).\n"

    with open("BENCHMARK.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print("BENCHMARK.md generated successfully.")

if __name__ == "__main__":
    generate_report()

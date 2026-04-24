from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

from memory_backends import ShortTermMemory, LongTermProfile, EpisodicMemory, SemanticMemory

load_dotenv()

class MemoryState(TypedDict):
    user_input: str
    messages: List[Dict[str, str]]
    user_profile: str
    episodes: str
    semantic_hits: str
    memory_budget: int
    llm_response: str
    enable_memory: bool

class ProfileUpdate(BaseModel):
    key: str = Field(description="Chìa khóa thông tin (VD: name, allergy, hobby, role)")
    value: str = Field(description="Giá trị thông tin (VD: Linh, đậu nành, đá bóng)")

class MemoryUpdates(BaseModel):
    profile_updates: List[ProfileUpdate] = Field(default_factory=list, description="Danh sách các thông tin cần cập nhật vào hồ sơ người dùng.")
    new_episode: Optional[str] = Field(default=None, description="Tóm tắt ngắn gọn sự kiện hoặc quyết định vừa xảy ra trong lượt hội thoại này. Chỉ tạo khi cần thiết.")

class MultiMemoryAgent:
    def __init__(self):
        self.short_term = ShortTermMemory(memory_budget=4000)
        self.long_term = LongTermProfile()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Build graph
        workflow = StateGraph(MemoryState)
        workflow.add_node("retrieve_memory", self.retrieve_memory)
        workflow.add_node("call_llm", self.call_llm)
        workflow.add_node("update_memory", self.update_memory)
        
        workflow.add_edge(START, "retrieve_memory")
        workflow.add_edge("retrieve_memory", "call_llm")
        workflow.add_edge("call_llm", "update_memory")
        workflow.add_edge("update_memory", END)
        
        self.app = workflow.compile()

    def retrieve_memory(self, state: MemoryState):
        if not state.get("enable_memory", True):
            return state

        # Retrieve semantic memory
        semantic_hits = self.semantic.search(state["user_input"], top_k=1)
        
        # Retrieve long term profile
        user_profile = self.long_term.get_profile()
        
        # Retrieve episodic memory
        episodes = self.episodic.get_episodes()
        
        return {
            "semantic_hits": semantic_hits,
            "user_profile": user_profile,
            "episodes": episodes
        }

    def call_llm(self, state: MemoryState):
        user_input = state["user_input"]
        enable_mem = state.get("enable_memory", True)
        
        # Lưu vào short-term
        self.short_term.add_message("user", user_input)
        
        system_prompt = "Bạn là một trợ lý AI hữu ích, nói tiếng Việt. "
        
        if enable_mem:
            system_prompt += "Dưới đây là các thông tin từ bộ nhớ của bạn:\n"
            system_prompt += f"\n--- USER PROFILE (Hồ sơ người dùng) ---\n{state.get('user_profile', 'Trống')}\n"
            system_prompt += f"\n--- RECENT EPISODES (Sự kiện gần đây) ---\n{state.get('episodes', 'Trống')}\n"
            
            if state.get("semantic_hits"):
                system_prompt += f"\n--- RELEVANT KNOWLEDGE (Kiến thức) ---\n{state['semantic_hits']}\n"
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Thêm lịch sử hội thoại (short-term)
        if enable_mem:
            for msg in self.short_term.get_messages()[:-1]: # Loại bỏ câu user cuối cùng vì nó đã nằm trong list
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
                    
        # Thêm câu hiện tại
        messages.append(HumanMessage(content=user_input))
                
        response = self.llm.invoke(messages)
        
        # Lưu câu trả lời
        self.short_term.add_message("assistant", response.content)
        
        return {"llm_response": response.content}

    def update_memory(self, state: MemoryState):
        if not state.get("enable_memory", True):
            return state
            
        extraction_prompt = f"""
        Bạn là một AI quản lý bộ nhớ. Hãy xem xét lượt hội thoại mới nhất:
        
        User: {state["user_input"]}
        Assistant: {state["llm_response"]}
        
        Nhiệm vụ của bạn:
        1. Trích xuất thông tin người dùng (tên, sở thích, tuổi, dị ứng...) để update Profile. Chú ý xử lý xung đột (nếu user sửa lại thông tin cũ, ví dụ "không phải A mà là B").
        2. Tóm tắt sự kiện nếu lượt này có một hành động/quyết định đáng nhớ để thêm vào Episodic Memory (VD: User nhờ debug một đoạn mã, User hỏi về hoàn tiền). Nếu chỉ là chào hỏi bình thường thì không cần.
        """
        
        llm_with_tool = self.llm.with_structured_output(MemoryUpdates)
        try:
            updates: MemoryUpdates = llm_with_tool.invoke([SystemMessage(content=extraction_prompt)])
            
            if updates.profile_updates:
                for p in updates.profile_updates:
                    self.long_term.update_fact(p.key, p.value)
                    
            if updates.new_episode:
                self.episodic.add_episode(updates.new_episode)
        except Exception as e:
            print(f"Update memory failed: {e}")
            
        return state

    def invoke(self, user_input: str, enable_memory: bool = True):
        state = {
            "user_input": user_input,
            "enable_memory": enable_memory
        }
        result = self.app.invoke(state)
        return result["llm_response"]

    def reset_all(self):
        self.short_term.clear()
        self.long_term.clear()
        self.episodic.clear()
        self.semantic.clear()

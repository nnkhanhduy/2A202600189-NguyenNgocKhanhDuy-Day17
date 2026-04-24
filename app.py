import streamlit as st
import os
from dotenv import load_dotenv
from agent_graph import MultiMemoryAgent
import json

# Set page config
st.set_page_config(page_title="Multi-Memory Agent Test UI", layout="wide")

# Load environment variables
load_dotenv()

# Initialize Agent in Session State
if "agent" not in st.session_state:
    st.session_state.agent = MultiMemoryAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for memory management and API Key
with st.sidebar:
    st.title("⚙️ Cấu hình Agent")
    
    # Toggle memory
    enable_memory = st.toggle("Kích hoạt bộ nhớ đa tầng", value=True)
    if enable_memory != st.session_state.get("enable_memory", True):
        st.session_state.enable_memory = enable_memory
        st.toast(f"Đã {'bật' if enable_memory else 'tắt'} bộ nhớ!")
    
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        # Re-init agent if key changes
        if st.button("Cập nhật API Key"):
            st.session_state.agent = MultiMemoryAgent()
            st.success("Đã cập nhật API Key!")

    st.divider()
    
    if st.button("🗑️ Reset toàn bộ bộ nhớ"):
        st.session_state.agent.reset_all()
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.subheader("📋 Trạng thái bộ nhớ hiện tại")
    
    with st.expander("💬 Short-term Memory (Chat History)"):
        st.write(f"Budget: {st.session_state.agent.short_term.memory_budget} tokens")
        st.json(st.session_state.agent.short_term.messages)

    with st.expander("👤 Long-term Profile"):
        profile = st.session_state.agent.long_term.profile_data
        st.json(profile)
    
    with st.expander("🎬 Episodic Memory"):
        episodes = st.session_state.agent.episodic.episodes
        st.json(episodes)
        
    with st.expander("🧠 Semantic Memory (FAQs)"):
        st.write("Dữ liệu mẫu đã nạp sẵn:")
        st.info("1. Lỗi docker port\n2. Chính sách hoàn tiền\n3. Đổi mật khẩu")

# Main Chat Interface
st.title("🤖 Multi-Memory Agent")
st.caption("Agent sử dụng LangGraph với 4 tầng bộ nhớ: Short-term, Long-term, Episodic, Semantic")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Nhập tin nhắn..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                # Use session state for enable_memory
                mem_on = st.session_state.get("enable_memory", True)
                response = st.session_state.agent.invoke(prompt, enable_memory=mem_on)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Lỗi: {e}")
                
    # Rerun to update sidebar memory displays
    st.rerun()

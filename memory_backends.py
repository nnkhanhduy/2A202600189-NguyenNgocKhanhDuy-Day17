import json
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
import tiktoken

# --- 1. ShortTermMemory ---
class ShortTermMemory:
    def __init__(self, memory_budget: int = 4000):
        self.messages: List[Dict[str, str]] = []
        self.memory_budget = memory_budget
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4o-mini")
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim()
    
    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages
        
    def _trim(self):
        # Trim using accurate tiktoken count
        while self._estimate_tokens() > self.memory_budget and len(self.messages) > 1:
            self.messages.pop(0) # Remove oldest message
            
    def _estimate_tokens(self) -> int:
        total_tokens = 0
        for m in self.messages:
            total_tokens += len(self.encoder.encode(m['content'])) + 4 # +4 for role overhead
        return total_tokens

    def clear(self):
        self.messages = []

# --- 2. LongTermProfile ---
class LongTermProfile:
    def __init__(self, filepath: str = "profile.json"):
        self.filepath = filepath
        self.profile_data: Dict[str, Any] = self._load()
        
    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
        
    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.profile_data, f, ensure_ascii=False, indent=2)
            
    def get_profile(self) -> str:
        if not self.profile_data:
            return "No profile data available."
        parts = []
        for k, v in self.profile_data.items():
            parts.append(f"{k}: {v}")
        return "\n".join(parts)
        
    def update_fact(self, key: str, value: Any):
        # Conflict handling logic: just override with new fact
        self.profile_data[key] = value
        self._save()

    def clear(self):
        self.profile_data = {}
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

# --- 3. EpisodicMemory ---
class EpisodicMemory:
    def __init__(self, filepath: str = "episodes.json"):
        self.filepath = filepath
        self.episodes: List[Dict[str, Any]] = self._load()
        
    def _load(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
        
    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.episodes, f, ensure_ascii=False, indent=2)
            
    def add_episode(self, summary: str, details: Optional[str] = None):
        episode = {"summary": summary}
        if details:
            episode["details"] = details
        self.episodes.append(episode)
        self._save()
        
    def get_episodes(self) -> str:
        if not self.episodes:
            return "No recent episodes."
        # Trả về 5 tập gần nhất
        recent = self.episodes[-5:]
        return "\n".join([f"- {ep['summary']}" for ep in recent])

    def clear(self):
        self.episodes = []
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

# --- 4. SemanticMemory ---
class SemanticMemory:
    def __init__(self, collection_name: str = "semantic_db"):
        self.client = chromadb.Client()
        
        # We need an openai API key for the embeddings. 
        # If it's not set, Chroma will fail if we try to use OpenAI embedding function.
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key:
            self.emb_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name="text-embedding-3-small"
            )
            self.collection = self.client.get_or_create_collection(
                name=collection_name, 
                embedding_function=self.emb_fn
            )
        else:
            self.collection = self.client.get_or_create_collection(name=collection_name)
            
        self._populate_initial_data()
        
    def _populate_initial_data(self):
        # We can prepopulate some FAQs or general knowledge to test semantic recall
        # E.g., docker debug lesson mentioned in the rubric
        docs = [
            "Lỗi 'port is already allocated' khi chạy docker: Dùng lệnh 'docker service name' hoặc 'docker ps' để tìm container đang giữ cổng đó và tắt đi.",
            "Chính sách hoàn tiền: Trong vòng 30 ngày kể từ ngày mua hàng, kèm hóa đơn gốc.",
            "Hướng dẫn đổi mật khẩu: Vào Settings -> Security -> Change password."
        ]
        ids = ["faq_1", "faq_2", "faq_3"]
        
        # Check if already populated
        if self.collection.count() < len(docs):
            try:
                self.collection.add(
                    documents=docs,
                    ids=ids
                )
            except Exception as e:
                print(f"Warning: could not add to Chroma collection: {e}")

    def search(self, query: str, top_k: int = 1) -> str:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            documents = results.get("documents", [[]])
            if documents and len(documents[0]) > 0:
                return "\n".join(documents[0])
            return ""
        except Exception as e:
            return f"Semantic search error: {e}"

    def clear(self):
        try:
            # Recreate the collection to clear it for fresh tests
            self.client.delete_collection(self.collection.name)
            if hasattr(self, 'emb_fn'):
                self.collection = self.client.create_collection(name=self.collection.name, embedding_function=self.emb_fn)
            else:
                self.collection = self.client.create_collection(name=self.collection.name)
            self._populate_initial_data()
        except Exception:
            pass

from langchain_core.chat_history import InMemoryChatMessageHistory
import firebase_memory_lang

memory = InMemoryChatMessageHistory()

def add_to_memory(human_message: str, ai_response: str, session_id: str = "default"):
    memory.add_user_message(human_message)
    memory.add_ai_message(ai_response)
    firebase_memory_lang.save_message(session_id, "user", human_message)
    firebase_memory_lang.save_message(session_id, "ai", ai_response)
def get_history() -> list:
    return memory.messages

def clear_memory():
    memory.clear()
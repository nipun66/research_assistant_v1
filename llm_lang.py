from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GEMINI_API_KEY2"),
    )

def get_answer(user_query: str, search_result: list, chat_history: list, summary: str = "") -> str:
    llm = get_llm()
    results_text = "\n\n".join([
        f"Source {i+1}: {r['title']}\n{r['snippet']}\nURL: {r['url']}"
        for i, r in enumerate(search_result)
    ])
    history_text = "\n".join([
        f"{'User' if msg.type == 'human' else 'Assistant'}: {msg.content}"
        for msg in chat_history[-20:]
    ])
    summary_text = f"Conversation summary so far:\n{summary}\n\n" if summary else ""
    messages = [
        SystemMessage(content="""You are an intelligent conversational research assistant. First understand what the user actually wants before responding. If the user is greeting you or making small talk, respond naturally and do not use search results. If the user asks a simple question, answer directly and concisely using the search results. If the user asks a complex research question, break it into sub-topics, address each using relevant sources, then give a clear summary. If the user is following up on something, use the conversation history to understand context. Always cite sources where relevant using (Source 1), (Source 2) etc. Never make up information not found in the search results. Keep your tone clear, warm and direct."""),
        HumanMessage(content=f"""
{summary_text}Recent conversation:
{history_text}

Search results:
{results_text}

User's question: {user_query}

Please answer based on the search results and conversation context above.
""")
    ]
    response = llm.invoke(messages)
    if isinstance(response.content, list):
        return " ".join([block["text"] for block in response.content if isinstance(block, dict) and "text" in block])
    return str(response.content)

def summarize_conversation(messages: list) -> str:
    llm = get_llm()
    history_text = "\n".join([
        f"{'User' if msg.type == 'human' else 'Assistant'}: {msg.content}"
        for msg in messages
    ])
    response = llm.invoke([
        SystemMessage(content="You are a summarization assistant. Summarize the following conversation in 3-5 sentences. Focus on the main topics discussed, key questions asked, and important answers given. Be concise."),
        HumanMessage(content=f"Conversation:\n{history_text}")
    ])
    if isinstance(response.content, list):
        return " ".join([block["text"] for block in response.content if isinstance(block, dict) and "text" in block])
    return str(response.content)
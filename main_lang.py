import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import firebase_memory_lang
import  uuid
load_dotenv()
from llm_lang import get_answer, summarize_conversation

import lang_memory
from search_lang import search_web
app = FastAPI()
SESSION_ID=str(uuid.uuid4())

class QueryRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.post("/search")
async def handle_search(request: QueryRequest):
    user_query = request.message
    chat_history = lang_memory.get_history()
    search_result = await search_web(user_query)
    summary = firebase_memory_lang.load_summary(SESSION_ID)
    answer = get_answer(user_query, search_result, chat_history, summary)
    lang_memory.add_to_memory(user_query, answer, SESSION_ID)
    updated_history = lang_memory.get_history()
    if len(updated_history) >= 4:
        new_summary = summarize_conversation(updated_history)
        firebase_memory_lang.save_summary(SESSION_ID, new_summary)
    return {
        "answer": answer,
        "sources": search_result,
    }
@app.get("/history")
async def get_history():
    messages = firebase_memory_lang.load_messages("default_user")
    return {"messages": messages}
@app.get("/sessions")
async def get_sessions():
    sessions = firebase_memory_lang.list_sessions()
    return {"sessions": sessions}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    messages = firebase_memory_lang.load_messages(session_id)
    return {"messages": messages}
@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    firebase_memory_lang.delete_session(session_id)
    return {"status": "deleted"}
@app.get("/new_chat")
@app.post("/new-session")
async def new_session():
    global SESSION_ID
    SESSION_ID = str(uuid.uuid4())
    lang_memory.clear_memory()
    return {"session_id": SESSION_ID}




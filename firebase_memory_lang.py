import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

if not firebase_admin._apps:
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
    else:
        cred = credentials.Certificate(os.getenv("FIREBASE_KEY_PATH", "service-account.json"))
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_message(session_id: str, role: str, content: str):
    db.collection("conversations")\
      .document(session_id)\
      .collection("messages")\
      .add({
          "role": role,
          "content": content,
          "timestamp": firestore.SERVER_TIMESTAMP
      })

def load_messages(session_id: str) -> list:
    messages = db.collection("conversations")\
                 .document(session_id)\
                 .collection("messages")\
                 .order_by("timestamp")\
                 .stream()
    return [
        {"role": m.to_dict()["role"], "content": m.to_dict()["content"]}
        for m in messages
    ]

def list_sessions() -> list:
    result = []
    
    # get all known session IDs by listing subcollection parents
    collections = db.collection("conversations").list_documents()
    found = [doc.id for doc in collections]
    
    if not found:
        found = ["default"]
    
    for session_id in found:
        messages = db.collection("conversations")\
                     .document(session_id)\
                     .collection("messages")\
                     .order_by("timestamp")\
                     .limit(1)\
                     .stream()
        first_msg = next(messages, None)
        if first_msg:
            preview = first_msg.to_dict().get("content", "")[:60]
            result.append({
                "session_id": session_id,
                "preview": preview
            })
    return result
def delete_session(session_id: str):
    messages = db.collection("conversations")\
                 .document(session_id)\
                 .collection("messages")\
                 .stream()
    for msg in messages:
        msg.reference.delete()
    db.collection("conversations").document(session_id).delete()
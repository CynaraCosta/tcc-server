from ..connection import db
from ..utils.loadJson import load_json

def conversationInsert(conversationJsonPath):
    conversation = load_json(conversationJsonPath)
    db.conversations.insert_one(conversation)
    print(f"Conversa {conversation['_id']} inserida com sucesso!")
from ..connection import db
import uuid
from ...gemini.gemini import query_data

collection = db['conversations']


def get_or_create_conversation(doctor_id, conversation_id=None):
    if conversation_id:
        conversation = collection.find_one({"_id": conversation_id})
        if conversation:
            return collection.find_one({"_id": conversation_id})

    new_conversation_id = str(uuid.uuid4())
    conversation = {
        "_id": new_conversation_id,
        "doctor_id": doctor_id,
        "messages": []
    }
    collection.insert_one(conversation)
    return collection.find_one({"_id": new_conversation_id})


def add_message_to_conversation(conversation_id, sender, message, timestamp, doctor_id):
    new_message = {
        "timestamp": timestamp,
        "sender": sender,
        "message": message,
    }

    collection.update_one(
        {"_id": conversation_id},
        {"$push": {"messages": new_message}}
    )


def generate_rag_response(user_question):
    response = query_data(user_question)[0]
    return response

def get_conversations():
    conversations = collection.find()

    response = []
    for conversation in conversations:
        if conversation['messages']:
            first_message = conversation['messages'][0]
            conversation_id = conversation['_id']
            response.append({
                'title': first_message['message'],
                'icon': 'message',
                'deeplink': f'/chat?id={conversation_id}'
            })

    return response

def get_messages_by_conversation_id(conversation_id):
    conversations = collection.find()
    for conversation in conversations:
        if conversation['_id'] == conversation_id:
            return conversation['messages']
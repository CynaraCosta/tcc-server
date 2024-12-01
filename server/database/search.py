from .connection import db
from embedding import generate_embedding

query = "João da Silva"
query_embedding = generate_embedding(query)
collection = db.patients

result = collection.find()

def search_in_field(field, vector, index, k=5, num_candidates=100, limit=10):
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "queryVector": vector,  
                "path": field,
                "numCandidates": num_candidates,
                "limit": limit,
                "index": index,
            }
        },
        {
            "$project": {
                "_id": 1,
                "patient_info.name": 1,
                # "medical_history": 1,
                # "consultations": 1,
                # "vaccine_info": 1,
                "search_score": {"$meta": "vectorSearchScore"}
            }
        }
    ])

    return list(results)

results_consultations = search_in_field("medical_history_embedding", query_embedding, "patient_medical_history")
print(list(results_consultations))



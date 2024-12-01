from .connection import db
from embedding import generate_embedding

query = "O paciente João da Silva tem alergia a algo?"
query_embedding = generate_embedding(query)
collection = db.patients

result = collection.find()

def search_in_field(field, vector, index, k=5, num_candidates=100, limit=5):
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
                "patient_info": 1,
                "medical_history": 1,
                "consultations": 1,
                "vaccine_info": 1,
                "search_score": {"$meta": "vectorSearchScore"}
            }
        }
    ])

    return list(results)

results_consultations = search_in_field("patient_embeddings", query_embedding, "patient_embeddings_search")
print(list(results_consultations))



from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import RetrievalQA
from config import Config
from database.connection import db
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.json_loader import JSONLoader
import json

key = Config.GEMINI_TOKEN

chat_model = ChatGoogleGenerativeAI(google_api_key=key, model="gemini-1.5-flash-latest")
embedding_model = GoogleGenerativeAIEmbeddings(google_api_key=key, model="models/embedding-001")

def load_data():
    loader = DirectoryLoader(
        './patients_mocks',
        glob='./*.json',
        show_progress=True,
        loader_cls=JSONLoader,
        loader_kwargs={'jq_schema': '.content', 'text_content': False}
    )
    raw_data = loader.load()
    for doc in raw_data:
        if 'source' in doc.metadata:
            with open(doc.metadata['source'], 'r', encoding='utf-8') as f:
                json_content = json.load(f)
            
            patient_info = json_content.get('patient_info', {})
            medical_history = json_content.get('medical_history', {})
            consultations = json_content.get('consultations', [])
            vaccine_info = json_content.get('vaccine_info', {})
            
            all_content = json.dumps({
                "patient_info": patient_info,
                "medical_history": medical_history,
                "consultations": consultations,
                "vaccine_info": vaccine_info
            }, ensure_ascii=False)
            
            embedding = embedding_model.embed_query(all_content)
            
            document = {
                "_id": json_content.get('_id'),
                "doctor_id": json_content.get('doctor_id'),
                "patient_info": patient_info,
                "medical_history": medical_history,
                "consultations": consultations,
                "vaccine_info": vaccine_info,
                "patient_embeddings": embedding,
                "text": all_content
            }
            
            collection = db.patients
            collection.insert_one(document)

    print("Dados carregados e processados com sucesso!")
    

def query_data(query):
    collection = db.patients
    vectorStore = MongoDBAtlasVectorSearch(collection, embedding_model, index_name='langchain_patients_vector_search_index', embedding_key='patient_embeddings')
    docs = vectorStore.similarity_search(query, K=5)
    as_output = docs[0].page_content
    retriever = vectorStore.as_retriever()
    qa = RetrievalQA.from_chain_type(chat_model, chain_type='stuff', retriever=retriever)
    retriver_output = qa.invoke(query)
    print(retriver_output)
    return as_output, retriver_output

if __name__ == '__main__':
    # load_data()
    # query_data("Faça um resumo do que acontece na última consulta do paciente Carlos Ribeiro Silva")
    pass


# {
#   "mappings": {
#     "dynamic": true,
#     "fields": {
#       "patient_embeddings": {
#         "dimensions": 768,
#         "similarity": "cosine",
#         "type": "knnVector"
#       }
#     }
#   }
# }
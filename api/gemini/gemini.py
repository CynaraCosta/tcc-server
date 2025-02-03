from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import RetrievalQA
from ..config import Config
from ..database.connection import db
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.json_loader import JSONLoader
import json
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import re



key = Config.GEMINI_TOKEN

chat_model = ChatGoogleGenerativeAI(
    google_api_key=key, model="gemini-1.5-flash-latest")
embedding_model = GoogleGenerativeAIEmbeddings(
    google_api_key=key, model="models/embedding-001")


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


def remove_markdown(text):
    """Removes Markdown formatting (like bold and italics) from the response."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove *italic*
    return text

def rewrite_prompt(query):
    rewrite_prompt = PromptTemplate.from_template(
        "Reescreva a seguinte consulta de forma objetiva e otimizada para busca sem adicionar informações extras:\n\n"
        "Consulta original: {query}\n"
        "Consulta otimizada:"
    )

    rewrite_chain = LLMChain(llm=chat_model, prompt=rewrite_prompt)
    improved_query = rewrite_chain.run(query)
    print(improved_query)
    improved_query = improved_query.strip().split("\n")[0]  
    return improved_query


def re_rank_documents(docs):
    # Sorts documents by relevance score if available.
    if all("score" in doc.metadata for doc in docs):
        return sorted(docs, key=lambda doc: doc.metadata["score"], reverse=True)
    return docs  


def query_data(query):
    collection = db.patients
    vectorStore = MongoDBAtlasVectorSearch(
        collection, embedding_model, index_name='langchain_patients_vector_search_index', embedding_key='patient_embeddings')

    # Query Expansion
    improved_query = rewrite_prompt(query)
    print(f"Improved Query: {improved_query}")

    prompt_template = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(
            """You are a helpful medical assistant. Based on the following patient information, 
            please follow these guidelines strictly:

            1. Only use information that is explicitly present in the provided patient records
            2. If you're unsure about any detail, acknowledge the uncertainty
            3. Do not make assumptions or infer information not present in the records
            4. If the information is not available in the patient's data, clearly state that
            5. Maintain a professional medical tone throughout your response
            6. Structure your response in a clear, clinical manner
            7. Detect the language of the question and respond in the same language
            8. Use appropriate medical terminology for the detected language
            9. If there ir previous conversation, take it into consideration 
            
            Patient Information:
            {context}

            User's new Question: {question}
            
            Please provide a clear and professional medical response, focusing only on factual information 
            from the patient's records. Use appropriate medical terminology where applicable, while 
            ensuring the response remains comprehensible and must be in the same language as the question."""
        )
    ])

    retriever = vectorStore.as_retriever()
    qa = RetrievalQA.from_chain_type(chat_model, chain_type='stuff', retriever=retriever,
                                     return_source_documents=True, chain_type_kwargs={'prompt': prompt_template})

     # First Retrieval
    retriever_output = qa.invoke(improved_query)

    # **Iterative Recovery** (if needed)
    if "não tenho informações suficientes" in retriever_output['result'].lower():
        print("Executando recuperação iterativa...")
        additional_docs = vectorStore.similarity_search(improved_query, K=10)  # Retrieve more documents
        ranked_additional_docs = re_rank_documents(additional_docs)

        retriever = vectorStore.as_retriever(documents=ranked_additional_docs)
        qa = RetrievalQA.from_chain_type(chat_model, chain_type='stuff', retriever=retriever, return_source_documents=True, chain_type_kwargs={'prompt': prompt_template})

        retriever_output = qa.invoke(improved_query)

    cleaned_output = remove_markdown(retriever_output['result'])
    print(cleaned_output)
    return cleaned_output


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

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import RetrievalQA
from config import Config
from database.connection import db
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain.docstore.document import Document
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
    loader_kwargs={'jq_schema':'.content', 'text_content': False}
    )
    raw_data = loader.load()
    processed_data = []
    for doc in raw_data:
        if 'source' in doc.metadata:
            with open(doc.metadata['source'], 'r', encoding='utf-8') as f:
                json_content = json.load(f)
            
            content = json.dumps(json_content, ensure_ascii=False)
            processed_data.append(Document(page_content=content, metadata=doc.metadata))
    
    collection = db.test_patients
    vectorStore = MongoDBAtlasVectorSearch.from_documents(processed_data, embedding_model, collection=collection)
    

def query_data(query):
    collection = db.test_patients
    vectorStore = MongoDBAtlasVectorSearch(collection, embedding_model, index_name='langchain_vectorSearch')
    docs = vectorStore.similarity_search(query, K=5)
    as_output = docs[0].page_content
    retriever = vectorStore.as_retriever()
    qa = RetrievalQA.from_chain_type(chat_model, chain_type='stuff', retriever=retriever)
    retriver_output = qa.invoke(query)
    print(retriver_output)
    return as_output, retriver_output

if __name__ == '__main__':
    # load_data()
    query_data("Qual foi a última consulta que o paciente João da Silva fez, e quais exames foram requisitados?")
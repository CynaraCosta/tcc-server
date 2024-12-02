from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from config import Config
from ..database.connection import db

key = Config.GEMINI_TOKEN

chat_model = ChatGoogleGenerativeAI(google_api_key=key, model="gemini-1.5-flash-latest")
embedding_model = GoogleGenerativeAIEmbeddings(google_api_key=key, model="models/embedding-001")
collection = db.patients
vectorStore = MongoDBAtlasVectorSearch(collection, embedding_model)
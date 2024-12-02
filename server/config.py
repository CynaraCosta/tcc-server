import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('mongoUri')
    HF_TOKEN = os.getenv('hfToken')
    GEMINI_TOKEN = os.getenv('geminiKey')
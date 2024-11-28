import pymongo
from config import Config

client = pymongo.MongoClient(Config.MONGO_URI)
db = client.tcc
collection = db.tests

items = collection.find()

for i in items:
    print(i)



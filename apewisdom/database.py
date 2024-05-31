from pymongo import MongoClient
import config

class MongoDBClient:
    def __init__(self, db_name, collection_name, uri=config.MONGO_URI):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_data(self, data):
        if isinstance(data, list):
            self.collection.insert_many(data)
        else:
            self.collection.insert_one(data)

    def find_data(self, query={}):
        return list(self.collection.find(query))

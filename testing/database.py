from pymongo import MongoClient

def get_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['reddit_stock_data']
    return db

def save_data_to_mongo(data):
    db = get_database()
    collection = db['posts']
    collection.insert_many(data.to_dict('records'))

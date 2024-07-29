import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
POSTS_COLLECTION_NAME = os.getenv('POSTS_COLLECTION_NAME')
COMMENTS_COLLECTION_NAME = os.getenv('COMMENTS_COLLECTION_NAME')

# Properly encode the username and password
encoded_username = quote_plus(MONGO_USERNAME)
encoded_password = quote_plus(MONGO_PASSWORD)

# Initialize MongoDB client
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@trendsage.svfhdvw.mongodb.net/{DB_NAME}?retryWrites=true&w=majority&authSource=admin"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
posts_collection = db[POSTS_COLLECTION_NAME]
comments_collection = db[COMMENTS_COLLECTION_NAME]

def cleanup_collection(collection):
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} documents from the {collection.name} collection.")

def main():
    cleanup_collection(posts_collection)
    cleanup_collection(comments_collection)

if __name__ == "__main__":
    main()

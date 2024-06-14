from urllib.parse import quote_plus
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env if not running in Streamlit
if not st.secrets:
    load_dotenv()

# Function to get secret or environment variable
def get_config_value(secret_section, secret_key, env_key):
    return st.secrets.get(secret_section, {}).get(secret_key, os.getenv(env_key))

# Reddit configuration
REDDIT_CLIENT_ID = get_config_value("reddit", "client_id", 'REDDIT_CLIENT_ID')
REDDIT_SECRET = get_config_value("reddit", "client_secret", 'REDDIT_SECRET')
REDDIT_USER_AGENT = get_config_value("reddit", "user_agent", 'REDDIT_USER_AGENT')
REDDIT_USERNAME = get_config_value("reddit", "username", 'REDDIT_USERNAME')
REDDIT_PASSWORD = get_config_value("reddit", "password", 'REDDIT_PASSWORD')

# MongoDB configuration
mongo_username = get_config_value("mongo", "username", 'MONGO_USERNAME')
mongo_password = get_config_value("mongo", "password", 'MONGO_PASSWORD')

if mongo_username is None or mongo_password is None:
    raise ValueError("MongoDB username or password is not set.")

username = quote_plus(mongo_username)
password = quote_plus(mongo_password)
MONGO_URI = get_config_value("mongo", "uri", f"mongodb+srv://{username}:{password}@trendsage.svfhdvw.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true")

DB_NAME = get_config_value("mongo", "db_name", 'DB_NAME')
COLLECTION_NAME = get_config_value("mongo", "collection_name", 'COLLECTION_NAME')

# API keys
NEWSAPI_KEY = get_config_value("newsapi", "key", 'NEWSAPI_KEY')
OPENAI_API_KEY = get_config_value("openai", "api_key", 'OPENAI_API_KEY')

from urllib.parse import quote_plus

REDDIT_CLIENT_ID = 'L5x_OBLY_HG9UxgxfOg69Q'
REDDIT_SECRET = '3f2igWO4Hdcu404B3KxVV81nE_hnsA'
REDDIT_USER_AGENT = 'python:StockPredictionApp:v1.0 (by /u/Stock_prediction)'
REDDIT_USERNAME = 'Stock_prediction'
REDDIT_PASSWORD = 'curry666666'

username = quote_plus('zhongjiayou1204')
password = quote_plus('Zjy2022@00')

MONGO_URI = f"mongodb+srv://{username}:{password}@trendsage.svfhdvw.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"

DB_NAME = "stock_trends"
COLLECTION_NAME = "trending_stocks"

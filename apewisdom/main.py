from pymongo import MongoClient
import ssl

uri = "mongodb+srv://zhongjiayou1204:Zjy2022%4000@trendsage.svfhdvw.mongodb.net/?retryWrites=true&w=majority&appName=TrendSage"
client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
db = client['test_db']
print(db.list_collection_names())

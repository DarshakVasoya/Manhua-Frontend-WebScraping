from pymongo import MongoClient

def get_mongo_client():
    uri = "mongodb://darshak:DarshakVasoya1310%40@165.232.60.4:27017/admin?authSource=admin"
    return MongoClient(uri)

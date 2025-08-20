# main.py
# This is a sample Python file for your project.

from pymongo import MongoClient

def main():
    # MongoDB connection string
    uri = "mongodb://darshak:DarshakVasoya1310%40@165.232.60.4:27017/admin?authSource=admin"
    # mongodb://darshak:<your_password>@165.232.60.4:27017/admin?authSource=admin
    client = MongoClient(uri)
    try:
        # Test connection
        db = client.admin
        server_info = client.server_info()
        print("Connected to MongoDB server:", server_info.get("version"))
    except Exception as e:
        print("Failed to connect to MongoDB:", e)
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()

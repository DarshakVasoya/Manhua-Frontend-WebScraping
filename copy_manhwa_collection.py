from mongodb_connection import get_mongo_client

def copy_collection():
    client = get_mongo_client()
    db = client.admin
    source_collection = db["manhwa"]
    target_collection = db["manhwa_backup"]
    docs = list(source_collection.find())
    if docs:
        target_collection.insert_many(docs)
        print(f"Copied {len(docs)} documents from 'manhwa' to 'manhwa_backup'.")
    else:
        print("No documents found in 'manhwa' collection.")
    client.close()

if __name__ == "__main__":
    copy_collection()

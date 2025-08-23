from datetime import datetime
from mongodb_connection import get_mongo_client

def update_existing_entries():
    client = get_mongo_client()
    db = client.admin  # Change if your DB is different
    collection = db["manhwa"]  # Change if your collection is different

    for doc in collection.find({"posted_on": {"$exists": True}}):
        posted_on = doc.get("posted_on")
        if posted_on:
            try:
                updated_at = datetime.strptime(posted_on, "%B %d, %Y")
            except Exception:
                updated_at = None
        else:
            updated_at = datetime.now()
        # Only update if not already present or different
        if updated_at and ("updated_at" not in doc or doc["updated_at"] != updated_at):
            collection.update_one({"_id": doc["_id"]}, {"$set": {"updated_at": updated_at}})
            print(f"Updated: {doc.get('name', doc['_id'])} -> updated_at: {updated_at}")
    client.close()

if __name__ == "__main__":
    update_existing_entries()

# cleanup_mongodb.py
from mongodb_connection import get_mongo_client


def main():
    client = get_mongo_client()
    db = client.admin  # Change to your target database if needed
    # Remove all documents from the 'manhwa' collection
    db["manhwa"].delete_many({})
    print("All documents removed from 'manhwa' collection.")
    # Optionally, drop the collection entirely:
    # db.drop_collection("manhwa")
    client.close()

if __name__ == "__main__":
    main()

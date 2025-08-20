# show_mongodb_data.py
from mongodb_connection import get_mongo_client


def main():
    client = get_mongo_client()
    db = client.admin  # Change to your target database if needed
    collection = db["manhwa"]  # Change to your target collection

    # Insert dummy data if collection is empty
    if collection.count_documents({}) == 0:
        dummy_data = [
            {"title": "Solo Leveling", "author": "Chugong"},
            {"title": "Tower of God", "author": "SIU"},
            {"title": "The Beginning After The End", "author": "TurtleMe"}
        ]
        collection.insert_many(dummy_data)
        print("Inserted dummy data into 'manhwa' collection.")

    print("Documents in 'manhwa' collection:")
    for doc in collection.find():
        print(doc)
    client.close()

if __name__ == "__main__":
    main()

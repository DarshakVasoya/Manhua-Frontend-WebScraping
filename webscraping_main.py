# webscraping_main.py
from mongodb_connection import get_mongo_client

# Example webscraping function (replace with your actual scraping logic)
def scrape_data():
    # Dummy scraped data
    return {"title": "Example Manhwa", "author": "Author Name"}


def main():
    client = get_mongo_client()
    db = client.admin  # Change to your target database if needed
    collection = db["manhwa"]  # Change to your target collection

    data = scrape_data()
    result = collection.insert_one(data)
    print(f"Inserted document with id: {result.inserted_id}")
    client.close()

if __name__ == "__main__":
    main()

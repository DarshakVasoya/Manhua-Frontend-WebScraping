
from mongodb_connection import get_mongo_client

def remove_duplicate_chapters():
    client = get_mongo_client()
    db = client.admin
    collection = db["manhwa"]
    manga_cursor = collection.find({})
    for manga in manga_cursor:
        chapters = manga.get("chapters", [])
        unique = {}
        for chapter in chapters:
            chapternum = chapter.get("chapternum")
            if chapternum:
                unique[chapternum] = chapter
        # Keep order by chapternum if possible
        deduped_chapters = list(unique.values())
        collection.update_one({"_id": manga["_id"]}, {"$set": {"chapters": deduped_chapters}})
        print(f"Updated manga: {manga.get('name', manga.get('url'))}, chapters deduped: {len(chapters)} -> {len(deduped_chapters)}")
    client.close()

if __name__ == "__main__":
    remove_duplicate_chapters()

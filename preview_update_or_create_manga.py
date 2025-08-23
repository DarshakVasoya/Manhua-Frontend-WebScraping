from datetime import datetime
from bs4 import BeautifulSoup
import requests
from mongodb_connection import get_mongo_client

def get_manga_links_and_latest_chapter(page_num):
    url = f"https://kingofshojo.com/manga/?page={page_num}&status=&type=&order=update"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    postbody = soup.find("div", class_="postbody")
    manga_list = []
    if postbody:
        for header in postbody.find_all(["h2", "h3"]):
            a = header.find("a", href=True)
            if a and a.text.strip() != "Manga Lists":
                manga_url = a["href"]
                chapter_div = header.find_next("div", class_="epxs")
                latest_chapter = None
                if chapter_div and "Chapter" in chapter_div.text:
                    try:
                        latest_chapter = int(chapter_div.text.strip().replace("Chapter", "").strip())
                    except Exception:
                        latest_chapter = None
                manga_list.append({"url": manga_url, "latest_chapter": latest_chapter})
    return manga_list

def preview_update_or_create_manga():
    print("Starting preview of manga updates...")
    client = get_mongo_client()
    db = client.admin
    collection = db["manhwa"]
    consecutive_matches = 0
    page_num = 1
    while True:
        print(f"Scraping page {page_num}...")
        manga_list = get_manga_links_and_latest_chapter(page_num)
        print(f"Found {len(manga_list)} manga on page {page_num}.")
        if not manga_list:
            print("No manga found. Exiting.")
            break
        for manga in manga_list:
            url = manga["url"]
            latest_chapter = manga["latest_chapter"]
            print(f"Checking manga: {url}")
            doc = collection.find_one({"url": url})
            if doc:
                db_last_chapter = None
                try:
                    db_last_chapter = int(str(doc.get("last_chapter", "0")).replace("Chapter", "").strip())
                except Exception:
                    db_last_chapter = 0
                if latest_chapter and latest_chapter > db_last_chapter:
                    print(f"Manga: {url}\n  Scraped last chapter: {latest_chapter}\n  DB last chapter: {db_last_chapter}\n  NEED TO UPDATE\n")
                    consecutive_matches = 0
                else:
                    print(f"Manga: {url}\n  Scraped last chapter: {latest_chapter}\n  DB last chapter: {db_last_chapter}\n  No update needed\n")
                    consecutive_matches += 1
            else:
                print(f"Manga: {url}\n  Scraped last chapter: {latest_chapter}\n  Not found in DB\n  NEED TO CREATE\n")
                consecutive_matches = 0
            if consecutive_matches >= 5:
                print("Last chapter matched for 5 consecutive manga. Stopping script.")
                client.close()
                return
        page_num += 1
    print("Preview complete.")
    client.close()

if __name__ == "__main__":
    preview_update_or_create_manga()

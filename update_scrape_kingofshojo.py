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
        listupd = postbody.find("div", class_="listupd")
        if listupd:
            for bs in listupd.find_all("div", class_="bs"):
                bsx = bs.find("div", class_="bsx")
                if bsx:
                    a = bsx.find("a", href=True)
                    manga_url = a["href"] if a else None
                    chapter_div = bsx.find("div", class_="epxs")
                    latest_chapter = None
                    if chapter_div and "Chapter" in chapter_div.text:
                        try:
                            latest_chapter = (chapter_div.text.strip())
                        except Exception:
                            latest_chapter = None
                    if manga_url:
                        manga_list.append({"url": manga_url, "latest_chapter": latest_chapter})
    return manga_list

def scrape_all_chapters_and_details(manga_url):
    response = requests.get(manga_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    chapters = []
    for li in soup.select("ul.clstyle > li"):
        chapter = {}
        a_tag = li.select_one(".eph-num a")
        if a_tag:
            chapter["link"] = a_tag["href"]
            chapternum_tag = a_tag.select_one(".chapternum")
            chapterdate_tag = a_tag.select_one(".chapterdate")
            chapter["chapternum"] = chapternum_tag.text.strip() if chapternum_tag else None
            chapter["chapterdate"] = chapterdate_tag.text.strip() if chapterdate_tag else None
            # Scrape images from chapter page
            try:
                ch_response = requests.get(chapter["link"])
                ch_response.raise_for_status()
                ch_soup = BeautifulSoup(ch_response.text, "html.parser")
                readerarea = ch_soup.find("div", id="readerarea")
                images = []
                if readerarea:
                    for img in readerarea.find_all("img", src=True):
                        src = img["src"]
                        if not src.startswith("https://i.ibb.co/"):
                            images.append(src)
                chapter["images"] = images
            except Exception as e:
                chapter["images"] = []
                chapter["image_error"] = str(e)
            chapters.append(chapter)
    def get_text(selector):
        tag = soup.select_one(selector)
        return tag.text.strip() if tag else None
    name = get_text(".entry-title") or get_text("h1")
    cover_image = None
    img_tag = soup.select_one(".thumb img, .seriestucontl .thumb img")
    if img_tag and img_tag.has_attr("src"):
        cover_image = img_tag["src"]
    rating = None
    rating_tag = soup.select_one(".rating-prc .num")
    if rating_tag:
        rating = rating_tag.text.strip()
    last_chap_tag = soup.select_one(".lastend .epcurlast")
    last_chapter = last_chap_tag.text.strip() if last_chap_tag else None
    description = None
    desc_tag = soup.select_one(".entry-content.entry-content-single")
    if desc_tag:
        description = desc_tag.text.strip()
    info = {}
    for row in soup.select(".infotable tr"):
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].text.strip().lower().replace(" ", "_")
            value = cols[1].text.strip()
            info[key] = value
    posted_on = None
    posted_tag = soup.select_one("td:-soup-contains('Posted On') + td time")
    if posted_tag:
        posted_on = posted_tag.text.strip()
    elif "posted_on" in info:
        posted_on = info["posted_on"]
    views = None
    views_tag = soup.select_one(".ts-views-count")
    if views_tag:
        views = views_tag.text.strip()
    elif "views" in info:
        views = info["views"]
    genres = []
    genre_tags = soup.select(".seriestugenre a")
    for g in genre_tags:
        genres.append(g.text.strip())
    updated_at = None
    if posted_on:
        try:
            updated_at = datetime.strptime(posted_on, "%B %d, %Y")
        except Exception:
            updated_at = datetime.now()
    else:
        updated_at = datetime.now()
    manga_details = {
        "cover_image": cover_image,
        "name": name,
        "rating": rating,
        "last_chapter": last_chapter,
        "description": description,
        "alternative": info.get("alternative"),
        "status": info.get("status"),
        "type": info.get("type"),
        "released": info.get("released"),
        "author": info.get("author"),
        "posted_on": posted_on,
        "updated_at": updated_at,
        "views": views,
        "genres": genres,
        "url": manga_url,
        "chapters": chapters
    }
    return manga_details
def scrape_specific_chapters(manga_url, latest_chapter, db_last_chapter):
    response = requests.get(manga_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    chapters = []
    for li in soup.select("ul.clstyle > li"):
        chapter = {}
        a_tag = li.select_one(".eph-num a")
        if a_tag:
            chapter["link"] = a_tag["href"]
            chapternum_tag = a_tag.select_one(".chapternum")
            chapterdate_tag = a_tag.select_one(".chapterdate")
            chapter["chapternum"] = chapternum_tag.text.strip() if chapternum_tag else None
            chapter["chapterdate"] = chapterdate_tag.text.strip() if chapterdate_tag else None
            if db_last_chapter == chapter["chapternum"]:
                break  
            # it will make list of chapters scrape for new one
        # Scrape images from chapter page
            try:
                ch_response = requests.get(chapter["link"])
                ch_response.raise_for_status()
                ch_soup = BeautifulSoup(ch_response.text, "html.parser")
                readerarea = ch_soup.find("div", id="readerarea")
                images = []
                if readerarea:
                    for img in readerarea.find_all("img", src=True):
                        src = img["src"]
                        if not src.startswith("https://i.ibb.co/"):
                            images.append(src)
                chapter["images"] = images
            except Exception as e:
                chapter["images"] = []
                chapter["image_error"] = str(e)
            chapters.append(chapter)
            
    last_chap_tag = soup.select_one(".lastend .epcurlast")
    last_chapter = last_chap_tag.text.strip() if last_chap_tag else None

    posted_on = None
    posted_tag = soup.select_one("td:-soup-contains('Posted On') + td time")
    if posted_tag:
        posted_on = posted_tag.text.strip()
    elif "posted_on" in info:
        posted_on = info["posted_on"]

    updated_at = None
    if posted_on:
        try:
            updated_at = datetime.strptime(posted_on, "%B %d, %Y")
        except Exception:
            updated_at = datetime.now()
    else:
        updated_at = datetime.now()
        
    manga_details = {
        
        "last_chapter": last_chapter,
        "posted_on": posted_on,
        "updated_at": updated_at,
        "chapters": chapters
    }
    return manga_details

def create_new_manga_entries():
    print("Starting manga entry creation/update...")
    total_created = 0
    total_updated = 0
    client = get_mongo_client()
    db = client.admin
    collection = db["manhwa_backup"]
    page_num = 1
    consecutive_no_update = 0
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
            if not doc:
                print(f"Manga not found in DB. Creating new entry for: {url}")
                manga_details = scrape_all_chapters_and_details(url)
                collection.insert_one(manga_details)
                print(f"Created new manga entry: {url}")
                total_created += 1
                consecutive_no_update = 0
            else:
                db_last_chapter = None
                try:
                    db_last_chapter = str(doc.get("last_chapter", "0"))
                except Exception:
                    db_last_chapter = ""
                # print(f"DB last chapter: {db_last_chapter}, Scraped last chapter: {latest_chapter}")
                if latest_chapter and latest_chapter != db_last_chapter:
                    print(f"Updating manga entry for: {url}")
                    manga_details = scrape_specific_chapters(url, latest_chapter, db_last_chapter)
                    # Append new chapters to existing chapters
                    existing_chapters = doc.get("chapters", [])
                    updated_chapters = manga_details["chapters"] + existing_chapters
                    collection.update_one(
                        {"url": url},
                        {"$set": {
                            "last_chapter": manga_details["last_chapter"],
                            "posted_on": manga_details["posted_on"],
                            "updated_at": manga_details["updated_at"],
                            "chapters": updated_chapters
                        }}
                    )
                    print(f"Updated manga entry: {url}")
                    total_updated += 1
                    consecutive_no_update = 0
                else:
                    print(f"No update needed for: {url}")
                    consecutive_no_update += 1
                    if consecutive_no_update >= 20:
                        print("No update needed for 20 consecutive manga. Exiting early.")
                        client.close()
                        return
        page_num += 1
    print(f"Script complete. Total created: {total_created}, Total updated: {total_updated}")
    client.close()

if __name__ == "__main__":
    create_new_manga_entries()

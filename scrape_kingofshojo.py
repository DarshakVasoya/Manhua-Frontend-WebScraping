import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from mongodb_connection import get_mongo_client

def get_manga_links(page_num):
    url = f"https://kingofshojo.com/manga/?page={page_num}&status=&type=&order=update"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    postbody = soup.find("div", class_="postbody")
    if postbody:
        # Find all a tags inside h2 or h3 inside postbody
        for header in postbody.find_all(["h2", "h3"]):
            a = header.find("a", href=True)
            if a and a.text.strip() != "Manga Lists":
                links.append(a["href"])
        # Also find direct a tags with manga links (sometimes not inside h2/h3)
        for a in postbody.find_all("a", href=True):
            href = a["href"]
            if href.startswith("https://kingofshojo.com/manga/") and href not in links and a.text.strip() != "Manga Lists":
                links.append(href)
    return links

def scrape_manga_details(manga_url):
    # Skip unwanted manga pages
    if manga_url == "https://kingofshojo.com/manga/list-mode":
        return None
    response = requests.get(manga_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    # Extract chapter list
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
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    def get_text(selector):
        tag = soup.select_one(selector)
        return tag.text.strip() if tag else None

    # Name
    name = get_text(".entry-title") or get_text("h1")
    if name == "Manga Lists":
        return None

    # Cover image
    cover_image = None
    img_tag = soup.select_one(".thumb img, .seriestucontl .thumb img")
    if img_tag and img_tag.has_attr("src"):
        cover_image = img_tag["src"]

    # Rating
    rating = None
    rating_tag = soup.select_one(".rating-prc .num")
    if rating_tag:
        rating = rating_tag.text.strip()

    # Last chapter
    last_chapter = None
    last_chap_tag = soup.select_one(".lastend .epcurlast")
    if last_chap_tag:
        last_chapter = last_chap_tag.text.strip()

    # Description
    description = None
    desc_tag = soup.select_one(".entry-content.entry-content-single")
    if desc_tag:
        description = desc_tag.text.strip()

    # Info table
    info = {}
    for row in soup.select(".infotable tr"):
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].text.strip().lower().replace(" ", "_")
            value = cols[1].text.strip()
            info[key] = value

    # Posted on
    posted_on = None
    posted_tag = soup.select_one("td:-soup-contains('Posted On') + td time")
    if posted_tag:
        posted_on = posted_tag.text.strip()
    elif "posted_on" in info:
        posted_on = info["posted_on"]

    # Views
    views = None
    views_tag = soup.select_one(".ts-views-count")
    if views_tag:
        views = views_tag.text.strip()
    elif "views" in info:
        views = info["views"]

    # Genres
    genres = []
    genre_tags = soup.select(".seriestugenre a")
    for g in genre_tags:
        genres.append(g.text.strip())

    # Parse posted_on to ISO format for updated_at
    from datetime import datetime
    updated_at = None
    if posted_on:
        try:
            updated_at = datetime.strptime(posted_on, "%B %d, %Y")
        except Exception:
            updated_at = None
    return {
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

def main():
    client = get_mongo_client()
    db = client.admin  # Change to your target database if needed
    collection = db["manhwa"]  # Change to your target collection
    # Ensure 'url' is a unique key
    collection.create_index("url", unique=True)
    error_collection = db["manhwa_errors"]
    error_collection.create_index("url", unique=True)

    progress_collection = db["scrape_progress"]
    # Resume from last progress if available
    last_progress = progress_collection.find_one({"_id": "last_scraped"})
    start_page = 1
    if last_progress and last_progress.get("url"):
        # Find the page number from the last scraped URL
        import re
        match = re.search(r"page=(\d+)", last_progress["url"])
        if match:
            start_page = int(match.group(1))
    for page_num in range(start_page, 90):
        print(f"Scraping page {page_num}")
        manga_links = get_manga_links(page_num)
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_link = {executor.submit(scrape_manga_details, link): link for link in manga_links}
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    details = future.result()
                    if details is None:
                        continue
                    # Store each manga immediately after scraping
                    try:
                        collection.insert_one(details)
                        print(f"Inserted manga: {details['name']} from {link}")
                        # Store progress after successful insert
                        progress_collection.update_one({"_id": "last_scraped"}, {"$set": {"url": link, "page": page_num}}, upsert=True)
                    except Exception as e:
                        from pymongo.errors import BulkWriteError
                        if isinstance(e, BulkWriteError):
                            print(f"Bulk write error: {e.details}")
                        else:
                            print(f"Error inserting manga details: {e}")
                    print(f"Scraped: {details['name']} from {link}")
                except Exception as e:
                    print(f"Error scraping {link}: {e}")
                    error_collection.update_one({"url": link}, {"$set": {"url": link, "error": str(e)}}, upsert=True)
    print("Scraping complete.")
    client.close()

if __name__ == "__main__":
    main()
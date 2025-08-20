import requests
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
        "views": views,
        "genres": genres,
        "url": manga_url
    }

def main():
    client = get_mongo_client()
    db = client.admin  # Change to your target database if needed
    collection = db["manhwa"]  # Change to your target collection

    page = 1
    manga_links = get_manga_links(page)
    manga_details_list = []
    for link in manga_links:
        details = scrape_manga_details(link)
        if details is None:
            continue
        manga_details_list.append(details)
        print(f"Scraped: {details['name']} from {link}")
    if manga_details_list:
        collection.insert_many(manga_details_list)
        print(f"Inserted {len(manga_details_list)} manga details from page {page}.")
    else:
        print("No manga found on page 1.")
    client.close()

if __name__ == "__main__":
    main()
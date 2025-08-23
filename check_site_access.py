import requests

def check_site_access():
    page_num=1;

    url = f"https://kingofshojo.com/manga/?page={page_num}&status=&type=&order=update"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        print("First 2000 characters of response:")
        print(response.text[:2000])
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        print("\nAll div classes on page:")
        for div in soup.find_all("div"):
            print(div.get("class"))
        print("\nAll h2/h3 tags:")
        for h in soup.find_all(["h2", "h3"]):
            print(h)
    except Exception as e:
        print(f"Error accessing site: {e}")

if __name__ == "__main__":
    check_site_access()

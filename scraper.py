import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin, urlparse
import tldextract
import sqlite3
import time
import random
from collections import deque
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading

ua = UserAgent()
HEADERS = {'User-Agent': ua.random}
SEED_URLS = [
    
   

    "https://edition.cnn.com/world",
    "https://www.nytimes.com/section/world",
    "https://www.washingtonpost.com/world/",
    "https://www.dw.com/en/top-stories/s-9097",
    "https://globalnews.ca/world/",
    "https://www.cbc.ca/news/world",
    "https://www.france24.com/en/world/",
    "https://www.scmp.com/news/world",
    "https://www.euronews.com/news/international",
    "https://www.abc.net.au/news/world"
]

MAX_ARTICLES = 10000
CRAWL_DELAY = (1, 3)
MAX_WORKERS = 10

visited = set()
article_hashes = set()
domains = set()
count = 0
queue = deque()
lock = threading.Lock()

# Setup SQLite
conn = sqlite3.connect("articles.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS articles")
cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    content TEXT
)
""")
conn.commit()

def get_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def normalize_and_filter(link, base_url):
    link = urljoin(base_url, link)
    parsed = urlparse(link)
    if parsed.scheme not in ('http', 'https'):
        return None
    domain = get_domain(link)
    return link if domain in domains else None

def fetch(url):
    try:
        headers = {'User-Agent': ua.random}
        response = requests.get(url, headers=headers, timeout=10)
        if 'text/html' in response.headers.get('Content-Type', ''):
            return response.text
    except Exception:
        return None
    return None

def extract_article(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else None
    paragraphs = soup.find_all('p')
    body = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
    return title, body

def save_article(url, title, body):
    global count
    content_hash = hashlib.md5((title + body).encode()).hexdigest()
    with lock:
        if content_hash in article_hashes or len(body.split()) < 200 or count >= MAX_ARTICLES:
            return
        try:
            cursor.execute("INSERT OR IGNORE INTO articles (url, title, content) VALUES (?, ?, ?)", (url, title, body))
            conn.commit()
            article_hashes.add(content_hash)
            count += 1
            print(f"[+] Saved ({count}): {url}")
        except Exception as e:
            print(f"[-] DB Error: {e}")

def crawl_page(url):
    with lock:
        if url in visited or count >= MAX_ARTICLES:
            return []
        visited.add(url)

    html = fetch(url)
    if not html:
        return []

    title, body = extract_article(html)
    if title and body:
        save_article(url, title, body)

    soup = BeautifulSoup(html, "html.parser")
    new_links = []
    for link in soup.find_all("a", href=True):
        abs_url = normalize_and_filter(link["href"], url)
        if abs_url:
            with lock:
                if abs_url not in visited:
                    new_links.append(abs_url)
    return new_links

def main():
    for seed in SEED_URLS:
        queue.append(seed)
        domains.add(get_domain(seed))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        while queue and count < MAX_ARTICLES:
            batch = []
            for _ in range(min(len(queue), MAX_WORKERS * 2)):
                url = queue.popleft()
                batch.append(url)

            future_to_url = {executor.submit(crawl_page, url): url for url in batch}
            for future in future_to_url:
                try:
                    result_links = future.result()
                    with lock:
                        queue.extend(result_links)
                except Exception as e:
                    print(f"[-] Crawl error: {e}")

            # Optional: short random delay between batches
            time.sleep(random.uniform(*CRAWL_DELAY))

    print("Scraping completed.")
    conn.close()

if __name__ == "__main__":
    main()

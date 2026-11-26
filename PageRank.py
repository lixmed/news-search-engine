import sqlite3
import json
import re
from bs4 import BeautifulSoup
import networkx as nx

DB_PATH = "articles.db"
OUTPUT_FILE = "pagerank.json"
# Load inverted index
with open('inverted_index_en.json', 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)

# Load word count
with open('word_counts_en.json', 'r', encoding='utf-8') as f:
    word_counts = json.load(f)  # تحميل البيانات الخاصة بالـ word counts

# Load PageRank
with open('pagerank.json', 'r', encoding='utf-8') as f:
    page_ranks = json.load(f)  # تحميل بيانات الـ PageRank

def extract_links_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = [a.get('href') for a in soup.find_all('a', href=True)]

    internal_links = []
    for link in links:
        if link.startswith('/'):  # If link starts with "/", it's an internal link
            internal_links.append(base_url + link)
        elif base_url in link:  # If link contains the base URL, it's internal
            internal_links.append(link)
    return internal_links

def build_link_graph(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, content FROM articles")
    rows = cursor.fetchall()
    conn.close()

    url_to_links = {}
    all_urls = set()

    for url, content in rows:
        links = extract_links_from_html(content, url)
        url_to_links[url] = links
        all_urls.add(url)

    # Only add edges if they are valid URLs
    graph = nx.DiGraph()
    for src, out_links in url_to_links.items():
        for dst in out_links:
            if dst in all_urls:  # Ensure destination URL is in the list of known URLs
                graph.add_edge(src, dst)

    return graph

def compute_pagerank(graph):
    if len(graph.nodes) == 0:
        return {}
    
    # Calculate PageRank with alpha = 0.85
    pagerank_scores = nx.pagerank(graph, alpha=0.85)
    return pagerank_scores

def save_pagerank(pagerank_dict):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(pagerank_dict, f, indent=2)

def get_documents(doc_ids, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in doc_ids)
    query = f"SELECT url, content FROM articles WHERE url IN ({placeholders})"
    cursor.execute(query, doc_ids)
    results = cursor.fetchall()
    conn.close()

    docs = []
    for url, content in results:
        wc = word_counts.get(url, 0)
        pr = page_ranks.get(url, 0.0)
        docs.append({
            'url': url,
            'content': content[:300] + "...",
            'word_counts': wc,
            'pagerank': pr
        })
    return docs

# Compute PageRank and save it
def compute_and_save_pagerank():
    print("[*] Building graph...")
    graph = build_link_graph()
    print(f"[*] Graph built with {len(graph.nodes())} nodes and {len(graph.edges())} edges")

    if len(graph.nodes()) == 0:
        print("[!] No nodes found in the graph. Check your data.")
        return

    print("[*] Computing PageRank...")
    pagerank_scores = compute_pagerank(graph)
    
    if not pagerank_scores:
        print("[!] PageRank scores are empty. Check the graph construction.")
    else:
        print(f"[*] PageRank computed for {len(pagerank_scores)} nodes.")
        save_pagerank(pagerank_scores)
        print(f"[✓] Done. PageRank saved to {OUTPUT_FILE}")

# Assuming you want to trigger the computation
compute_and_save_pagerank()

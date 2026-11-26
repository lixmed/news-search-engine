from flask import Flask, request, jsonify
import json
import sqlite3
from bs4 import BeautifulSoup
import networkx as nx
import difflib

app = Flask(__name__)

# --------------------------
# Load JSON Files
# --------------------------
with open('inverted_index_en.json', 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)

with open('word_counts_en.json', 'r', encoding='utf-8') as f:
    word_counts = json.load(f)

with open('pagerank.json', 'r', encoding='utf-8') as f:
    page_ranks = json.load(f)


# --------------------------
# Helper Functions
# --------------------------

# Approximate match for URL to word_count
def find_best_match(url):
    # تطبيع الرابط لإزالة أي / في النهاية أو www أو http/https
    def normalize(u):
        u = u.strip().lower()
        if u.endswith('/'):
            u = u[:-1]
        u = u.replace('https://', '').replace('http://', '').replace('www.', '')
        return u

    norm_url = normalize(url)
    # جرب التطابق المباشر بعد التطبيع
    for stored_url in word_counts:
        if normalize(stored_url) == norm_url:
            return word_counts[stored_url]

    # جرب التطابق الجزئي (إذا الرابط جزء من المفتاح)
    for stored_url in word_counts:
        if norm_url in normalize(stored_url) or normalize(stored_url) in norm_url:
            return word_counts[stored_url]

    # جرب المطابقة التقريبية
    best_score = 0
    best_url = None
    for stored_url in word_counts:
        score = difflib.SequenceMatcher(None, norm_url, normalize(stored_url)).ratio()
        if score > best_score:
            best_score = score
            best_url = stored_url
    if best_score > 0.6:  # This threshold might be too high
        return word_counts.get(best_url, 0)
    return 0  # Returns 0 if no match found


# Get articles from DB and enrich with metadata
def get_documents(doc_ids, db_path='articles.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in doc_ids)
    query = f"SELECT url, content FROM articles WHERE url IN ({placeholders})"
    cursor.execute(query, doc_ids)
    results = cursor.fetchall()
    conn.close()

    # استخراج الكلمة المطلوبة من الاستعلام إذا كانت موجودة في request
    search_word = None
    try:
        search_word = request.args.get('q', '').strip().lower()
        # إذا كان هناك أكثر من كلمة، نأخذ أول كلمة فقط
        if search_word:
            search_word = search_word.split()[0]
    except Exception:
        search_word = None

    docs = []
    for url, content in results:
        wc = find_best_match(url)
        if wc == 0:
            print(f"[!] URL not found in word_counts: {url}")
        pr = page_ranks.get(url, 0.0)
        # حساب عدد مرات تكرار الكلمة المطلوبة في نص المقال
        search_word_count = 0
        if search_word:
            # تحويل النص إلى حروف صغيرة وحساب التكرار بدقة
            content_lower = content.lower()
            search_word_count = content_lower.split().count(search_word)
        docs.append({
            'url': url,
            'content': content[:300] + "...",
            'word_counts': wc,
            'pagerank': pr,
            'search_word_count': search_word_count
        })
    return docs


# Extract internal links from article content
def extract_links_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = [a.get('href') for a in soup.find_all('a', href=True)]

    internal_links = []
    for link in links:
        if link.startswith('/'):
            internal_links.append("https://www.theguardian.com" + link)
        elif "https://www.theguardian.com" in link:
            internal_links.append(link)
    return internal_links


# Build the internal link graph from database
def build_link_graph(db_path='articles.db'):
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

    graph = nx.DiGraph()
    for src, out_links in url_to_links.items():
        for dst in out_links:
            if dst in all_urls:
                graph.add_edge(src, dst)

    return graph


# Compute PageRank from link graph
def compute_pagerank(graph):
    if len(graph.nodes) == 0:
        return {}
    pagerank_scores = nx.pagerank(graph, alpha=0.85)
    return pagerank_scores


# Save pagerank dict to file
def save_pagerank(pagerank_dict, output_file='pagerank.json'):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pagerank_dict, f, indent=2)


# --------------------------
# Routes
# --------------------------

@app.route('/compute_pagerank')
def compute_and_save_pagerank():
    print("[*] Building graph...")
    graph = build_link_graph()
    print(f"[*] Graph built with {len(graph.nodes())} nodes and {len(graph.edges())} edges")
    print("[*] Computing PageRank...")
    pagerank_scores = compute_pagerank(graph)
    print("[*] Saving PageRank to file...")
    save_pagerank(pagerank_scores)
    return jsonify({"message": "PageRank computed and saved to 'pagerank.json'"}), 200


@app.route('/')
def home():
    return '<h2>مرحبًا بك في محرك البحث المصغر!</h2><p>استخدم /search للبحث في المقالات.</p>'

@app.route('/search')
def search():
    query = request.args.get('q', '').lower().strip()
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    tokens = query.split()
    if not tokens:
        return jsonify({'results': []})

    doc_sets = [set(inverted_index.get(token, [])) for token in tokens]
    if not doc_sets:
        return jsonify({'results': []})

    common_doc_ids = list(set.intersection(*doc_sets)) if len(doc_sets) > 1 else list(doc_sets[0])

    if not common_doc_ids:
        return jsonify({'results': []})

    results = get_documents(common_doc_ids)
    return jsonify({'results': results})


# --------------------------
# Start App
# --------------------------

if __name__ == '__main__':
    app.run(debug=True)

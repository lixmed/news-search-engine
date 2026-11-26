import sqlite3
import re
import json
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(set)
        logging.info("InvertedIndex initialized")

    def preprocess(self, text):
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)  
        return words

    def build_index(self, documents):
        for doc_id, content in documents.items():
            words = self.preprocess(content)
            for word in words:
                self.index[word].add(doc_id)
        logging.info(f"Index built with {len(self.index)} terms")

    def save_index(self, filepath='inverted_index_en.json'):
        serializable = {k: list(v) for k, v in self.index.items()}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, ensure_ascii=False)
        logging.info(f"Index saved to {filepath}")

    def print_stats(self):
        total_terms = len(self.index)
        avg_docs_per_term = sum(len(v) for v in self.index.values()) / total_terms
        print(f"\nIndex Statistics:")
        print(f"Total unique terms: {total_terms}")
        print(f"Avg documents per term: {avg_docs_per_term:.2f}")

def fetch_documents(db_path='articles.db'):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, content FROM articles")  
        rows = cursor.fetchall()
        documents = {url: content for url, content in rows}
        conn.close()
        logging.info(f"✅ Fetched {len(documents)} documents from database")
        return documents
    except sqlite3.OperationalError as e:
        logging.error(f"❌ DB Error: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected Error: {e}")

def main():
    documents = fetch_documents()
    indexer = InvertedIndex()
    indexer.build_index(documents)
    indexer.save_index()
    indexer.print_stats()

if __name__ == "__main__":
    main()

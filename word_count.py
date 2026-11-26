import re
import json
import sqlite3
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnglishWordCounter:
    def __init__(self):
        # Change to store counts per document
        self.doc_word_counts = defaultdict(lambda: defaultdict(int))
        self.total_counter = Counter()
        logging.info("English WordCounter initialized")

    def preprocess(self, text):
        # Remove non-alphabetic chars, lowercase everything
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())  # matches words of any length
        return words

    def count_words(self, documents):
        for url, content in documents.items():
            words = self.preprocess(content)
            # Count words for this specific document
            doc_counter = Counter(words)
            self.doc_word_counts[url] = dict(doc_counter)
            # Update total counts
            self.total_counter.update(words)
        logging.info(f"Counted {sum(self.total_counter.values())} words across {len(documents)} documents")

    def save_counts(self, filepath='word_counts_en.json'):
        # Save the per-document word counts
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dict(self.doc_word_counts), f, ensure_ascii=False, indent=2)
        logging.info(f"Saved word counts to {filepath}")

    def print_stats(self, top_n=20):
        total = sum(self.total_counter.values())
        unique = len(self.total_counter)
        print(f"\nWord Stats:")
        print(f"Total words: {total}")
        print(f"Unique words: {unique}")
        print(f"\nTop {top_n} most common words:")
        for word, count in self.total_counter.most_common(top_n):
            print(f"{word}: {count}")

def fetch_documents(db_path='articles.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, content FROM articles")
    documents = {url: content for url, content in cursor.fetchall()}
    conn.close()
    logging.info(f"Fetched {len(documents)} documents from the database")
    return documents

if __name__ == "__main__":
    documents = fetch_documents()
    counter = EnglishWordCounter()
    counter.count_words(documents)
    counter.save_counts()
    counter.print_stats()
    
    print("\n========== Full Word Count Per URL ==========\n")
    for url, word_counts in counter.doc_word_counts.items():
        print(f"[+] URL: {url}")
        sorted_counts = sorted(word_counts.items(), key=lambda x: -x[1])
        for word, count in sorted_counts:
            print(f"    {word}: {count}")
        print()
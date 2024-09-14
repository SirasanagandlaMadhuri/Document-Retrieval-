import sqlite3
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        try:
            with self.conn:
                # Create tables
                self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    request_count INTEGER
                )''')
                self.conn.execute('''CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    published_at TEXT
                )''')
                # Create indexes
                self.conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title)')
                self.conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at)')
            logging.info("Database tables and indexes created successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}", exc_info=True)

    def get_user_request_count(self, user_id):
        try:
            cursor = self.conn.execute('SELECT request_count FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logging.error(f"Database query error: {e}", exc_info=True)
            return None

    def add_user(self, user_id):
        try:
            with self.conn:
                self.conn.execute('INSERT INTO users (id, request_count) VALUES (?, ?)', (user_id, 1))
            logging.info(f"User {user_id} added.")
        except sqlite3.Error as e:
            logging.error(f"Database insert error: {e}", exc_info=True)

    def update_user_request_count(self, user_id, count):
        try:
            with self.conn:
                self.conn.execute('UPDATE users SET request_count = ? WHERE id = ?', (count, user_id))
            logging.info(f"User {user_id} request count updated to {count}.")
        except sqlite3.Error as e:
            logging.error(f"Database update error: {e}", exc_info=True)

    def store_articles(self, articles):
        try:
            with self.conn:
                for article in articles:
                    self.conn.execute('INSERT OR REPLACE INTO articles (id, title, content, published_at) VALUES (?, ?, ?, ?)',
                                      (article['url'], article.get('title', ''), article.get('content', ''), article.get('publishedAt', '')))
            logging.info("Articles stored successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database insert error: {e}", exc_info=True)

    def search_articles(self, query_text, top_k, threshold):
        try:
            cursor = self.conn.execute('SELECT * FROM articles')
            articles = cursor.fetchall()

            if not articles:
                logging.info("No articles found in the database.")
                return []

            # Reformat articles as dicts
            articles = [{'id': row[0], 'title': row[1], 'content': row[2], 'published_at': row[3]} for row in articles]
            return rerank_articles(articles, query_text, top_k, threshold)
        except sqlite3.Error as e:
            logging.error(f"Database query error: {e}", exc_info=True)
            return []

    def get_highlighted_news(self):
        try:
            # Fetch highlighted news (example query for latest news)
            cursor = self.conn.execute('SELECT * FROM articles ORDER BY published_at DESC LIMIT 5')
            highlighted_news = cursor.fetchall()
            return [{'id': row[0], 'title': row[1], 'published_at': row[3]} for row in highlighted_news]
        except sqlite3.Error as e:
            logging.error(f"Database query error: {e}", exc_info=True)
            return []

def rerank_articles(articles, query_text, top_k, threshold):
    # Extract titles and create a list of documents
    titles = [article['title'] for article in articles]

    # Initialize the vectorizer
    vectorizer = TfidfVectorizer()

    # Vectorize the query text and articles
    documents = titles + [query_text]
    vectors = vectorizer.fit_transform(documents)

    # Compute similarity scores
    cosine_sim = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    # Add similarity score to articles
    for i, article in enumerate(articles):
        article['similarity_score'] = cosine_sim[i]

    # Filter and sort articles based on the threshold and top_k
    ranked_articles = [article for article in articles if article['similarity_score'] >= threshold]
    ranked_articles = sorted(ranked_articles, key=lambda x: x['similarity_score'], reverse=True)

    return ranked_articles[:top_k]
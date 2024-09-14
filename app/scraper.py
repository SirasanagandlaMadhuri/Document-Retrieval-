import time
import requests
import logging
from app.database import Database
from tenacity import retry, stop_after_attempt, wait_fixed
from requests.exceptions import HTTPError, RequestException
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Define constants
API_URL = 'http://newsapi.org/v2/top-headlines'
API_KEY = '47bc15726aca41ddb421394fabc0da4d'
RETRY_ATTEMPTS = 3
RETRY_WAIT = 2  # seconds

@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(RETRY_WAIT))
def scrape_news_articles(category=None, country=None):
    logging.info("Starting to scrape news articles...")
    try:
        params = {
            'apiKey': API_KEY,
            'language': 'en'
        }
        if category:
            params['category'] = category
        if country:
            params['country'] = country
        
        # Ensure at least one parameter is provided
        if not category and not country:
            params['category'] = 'general'  # Set a default category if none specified
            # Optionally, you might choose a default country, or leave it to show global news

        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses

        articles = response.json().get('articles', [])
        if not articles:
            logging.warning("No articles found in the response")

        # Store articles in the database
        database = Database()
        database.store_articles(articles)

        logging.info(f"Scraped {len(articles)} articles successfully.")

    except HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}", exc_info=True)
    except RequestException as req_err:
        logging.error(f"Request error occurred: {req_err}", exc_info=True)
    except Exception as e:
        logging.error(f"General error occurred: {e}", exc_info=True)

def start_scraping():
    while True:
        try:
            scrape_news_articles()  # Optionally, you can pass specific parameters here
        except Exception as e:
            logging.error("Exception in start_scraping", exc_info=True)
        time.sleep(3600)  # Run every hour

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

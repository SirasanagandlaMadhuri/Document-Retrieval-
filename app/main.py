from flask import Blueprint, request, jsonify, abort
import time
import random
import logging
from app.database import Database
from app.utils import log_inference_time, validate_search_parameters

main = Blueprint('main',__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@main.route('/health', methods=['GET'])
def health_check():
    logging.info("Health check endpoint hit")
    return jsonify({"status": "ok", "random": random.random()})

@main.route('/search', methods=['POST'])
def search():
    start_time = time.time()

    try:
        # Extract parameters
        data = request.get_json(force=True)
        user_id = data.get('user_id')
        text = data.get('text', '')
        top_k = data.get('top_k', 5)
        threshold = data.get('threshold', 0.7)

        # Validate parameters
        if not user_id:
            abort(400, description="user_id is required")

        validate_search_parameters({"top_k": top_k, "threshold": threshold})

        # Perform search logic
        results = Database().search_articles(text, top_k, threshold)

        if not results:
            # If no results, return default highlighted news and no articles message
            highlighted_news = Database().get_highlighted_news()
            return jsonify({
                "message": "No articles found for your search.",
                "highlighted_news": highlighted_news
            })

        inference_time = log_inference_time(start_time, "Search request")

        return jsonify({"results": results, "inference_time": inference_time})

    except ValueError as ve:
        logging.error(f"Validation error: {ve}", exc_info=True)
        abort(400, description=str(ve))
    except Exception as e:
        logging.error(f"Search error: {e}", exc_info=True)
        abort(500, description="Internal Server Error")
from flask import Flask
from flask_caching import Cache
import threading
import logging
from app.database import Database
from app.scraper import start_scraping

cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')  # Assuming config.Config contains the cache settings
    cache.init_app(app)

    # Initialize the database
    database = Database()

    # Start the background scraping thread
    def start_background_tasks():
        start_scraping()
    

    threading.Thread(target=start_background_tasks, daemon=True).start()

    # Import and register routes
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

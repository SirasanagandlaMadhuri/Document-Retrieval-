Document Retrieval System

This system is built using Flask as the backend framework, SQLite for database management, and Redis for caching to optimize performance. The backend handles API requests to retrieve relevant news articles based on query text and supports user rate limiting.
Components
1. API Design
	/health: Returns a random response to check if the API is active.
	/search: Accepts a user query and returns a list of top results based on specified parameters: text, top_k, and threshold.
		text: The search query text.
		top_k: The number of top results to return (default: 5).
		threshold: The minimum similarity score to filter results (default: 0.7).
		user_id: A unique identifier for each user. Request counts are tracked, and users are rate-limited to a maximum of 5 			requests.
2. Database Interaction
The system uses SQLite to store user request counts and news articles. Efficient indexing on article titles and publication dates ensures quick lookups.
Tables are users: Stores id and request_count.
	   articles: Stores id, title, content, and published_at.
Indexes on title and published_at improve the performance of retrievals.
3. Concurrency
Background Tasks are implemented in a separate thread at server startup to scrape news articles periodically and store them in the SQLite database.
4. Caching and Optimization
The system uses Redis for caching search results to ensure faster retrieval. Cached results for frequently accessed queries reduce the load on the database and improve response times.
5. Error Handling and Logging
Rate Limiting: Each user’s request count is tracked. If a user exceeds 5 requests, they receive an HTTP 429 error.

Advantages of Flask and Redis
Flask allows us to choose the components (such as database and caching mechanisms) that best suit the project.
Easy Integration: Flask easily integrates with tools like Flask-Caching and supports background threading for tasks like scraping.
Redis is an in-memory data store that provides faster read/write access compared to disk-based storage options, making it ideal for caching frequently accessed data.
Redis scales well with increased data load and is more efficient than alternatives like Memcached in this context.

Conclusion
The document retrieval system successfully meets the requirements of efficient document retrieval, caching, and concurrency.
The system is optimized for performance using Redis caching, and the searching to return the most relevant results.

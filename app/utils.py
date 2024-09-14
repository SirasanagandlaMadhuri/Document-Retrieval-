import time
import logging

def log_inference_time(start_time: float, action_name: str = "Request"):
    """Logs the time taken for a specific action."""
    elapsed_time = time.time() - start_time
    logging.info(f"{action_name} took {elapsed_time:.2f} seconds")
    return elapsed_time

def validate_search_parameters(params):
    top_k = params.get("top_k")
    threshold = params.get("threshold")

    if not (1 <= top_k <= 100):  # Ensure top_k is a valid number between 1 and 100
        raise ValueError("top_k must be between 1 and 100")

    if not (0 <= threshold <= 1):  # Ensure threshold is a valid similarity score
        raise ValueError("threshold must be between 0 and 1")

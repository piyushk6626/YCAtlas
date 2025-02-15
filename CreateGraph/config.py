# modules/config.py
import os
import logging
from dotenv import load_dotenv

def setup_logging():
    """
    Set up logging for the application.

    Returns:
        logging.Logger: The configured logger instance
    """
    logging.basicConfig(
        filename="logs/app.log",  # Store logs in a separate folder
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)

def load_env_vars():
    """
    Load environment variables from the .env file.

    Returns:
        dict: A dictionary containing the environment variables
    """
    load_dotenv()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    }

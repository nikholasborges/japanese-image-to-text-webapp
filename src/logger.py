import logging
import os

# Set up logging
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_FOLDER = os.path.join(BASE_DIR, "/src/logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

log_file = os.path.join(LOG_FOLDER, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)


def get_logger(name):
    return logging.getLogger(name)

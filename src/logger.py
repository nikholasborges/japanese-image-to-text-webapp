import logging
from src import settings

log_file = f"{settings.BASE_DIR}/src/logs/app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)


def get_logger(name):
    return logging.getLogger(name)

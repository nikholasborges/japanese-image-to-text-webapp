import os
import traceback
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from src.logger import get_logger

scheduler = BackgroundScheduler()
scheduler.start()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

logger = get_logger(__name__)


def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error when deleting file: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")


def clean_uploads():
    try:
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error when cleaning uploads: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")


def schedule_file_delete(file_path):
    try:
        scheduler.add_job(
            delete_file,
            "date",
            run_date=datetime.now() + timedelta(minutes=10),
            args=[file_path],
        )
    except Exception as e:
        logger.error(f"Error when scheduling file delete: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

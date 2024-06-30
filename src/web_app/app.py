import os
import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from src.web_app.utils import schedule_file_delete, clean_uploads
from src.text_extractor.app import TextExtractor
from src.logger import get_logger

flask_app = Flask(__name__)

# Configure upload folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
flask_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

logger = get_logger(__name__)


@flask_app.route("/")
def index():
    return render_template("index.html")


@flask_app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify(success=False, message="No file part")

        file = request.files["file"]
        if file.filename == "":
            return jsonify(success=False, message="No selected file")

        if file:
            file_path = os.path.join(flask_app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            file_url = url_for("uploaded_file", filename=file.filename)

            schedule_file_delete(file_path)

            return jsonify(
                success=True,
                message="File successfully uploaded",
                file_url=file_url,
                filename=file.filename,
            )

        return jsonify(success=False, message="File upload failed")

    except Exception as e:
        logger.error(f"Error when uploading file: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify(
            success=False, message="Internal server error, please try again."
        )


@flask_app.route("/upload_cropped/<filename>", methods=["POST"])
def upload_cropped_file(filename):
    try:
        if "croppedImage" not in request.files:
            return jsonify(success=False, message="No cropped image part")

        file = request.files["croppedImage"]
        if file.filename == "":
            return jsonify(success=False, message="No selected file")

        if file:
            file_path = os.path.join(flask_app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            file_url = url_for("uploaded_file", filename=filename)

            schedule_file_delete(file_path)

            return jsonify(
                success=True,
                message="Cropped file successfully uploaded",
                file_url=file_url,
                filename=filename,
            )

        return jsonify(success=False, message="Cropped file upload failed")

    except Exception as e:
        logger.error(f"Error when uploading cropped file: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify(
            success=False, message="Internal server error, please try again."
        )


@flask_app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(flask_app.config["UPLOAD_FOLDER"], filename)


@flask_app.route("/process/<path:filename>", methods=["POST"])
def process_file(filename):
    try:
        file_path = os.path.join(flask_app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(file_path):
            return jsonify(
                success=False, message="The image was not found, please reupload it."
            )

        extractor_app = TextExtractor()
        processed_text = extractor_app.run(file_path)

        if not processed_text:
            return jsonify(
                success=False, message="Processing failed,  please try again."
            )

        return jsonify(
            success=True,
            message="Processing completed successfully",
            result=processed_text,
        )

    except Exception as e:
        logger.error(f"Error when processing file: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify(
            success=False, message="Internal server error, please try again."
        )


def run_web_app(debug=False):
    flask_app.run(debug)
    clean_uploads()

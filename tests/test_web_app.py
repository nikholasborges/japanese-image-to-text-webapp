import os
import tempfile
import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock

from src.web_app.app import flask_app


class TestWebApp(unittest.TestCase):

    def setUp(self):
        self.app = flask_app
        self.client = self.app.test_client()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app.config["TESTING"] = True
        self.app.config["UPLOAD_FOLDER"] = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("src.web_app.app.schedule_file_delete")
    def test_upload_file_no_file_part(self, mock_schedule_file_delete):
        data = {}
        response = self.client.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertEqual(json_data["message"], "No file part")
        mock_schedule_file_delete.assert_not_called()

    @patch("src.web_app.app.schedule_file_delete")
    def test_upload_file_no_selected_file(self, mock_schedule_file_delete):
        data = {"file": (BytesIO(b"dummy data"), "")}
        response = self.client.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertEqual(json_data["message"], "No selected file")
        mock_schedule_file_delete.assert_not_called()

    @patch("src.web_app.app.schedule_file_delete")
    def test_upload_file_success(self, mock_schedule_file_delete):
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"Test file content")
            temp_file.seek(0)
            data = {"file": (temp_file, "test_image.png")}
            response = self.client.post(
                "/upload", data=data, content_type="multipart/form-data"
            )
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data["success"])
            self.assertIn("file_url", json_data)
            mock_schedule_file_delete.assert_called_once()

    @patch("src.web_app.app.schedule_file_delete")
    def test_upload_cropped_file(self, mock_schedule_file_delete):
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"Test file content")
            temp_file.seek(0)
            data = {"croppedImage": (temp_file, "test_image.png")}
            response = self.client.post(
                f"/upload_cropped/test_image.png",
                data=data,
                content_type="multipart/form-data",
            )
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data["success"])
            self.assertIn("file_url", json_data)
            mock_schedule_file_delete.assert_called_once()

    def test_uploaded_file(self):
        with open(
            os.path.join(self.app.config["UPLOAD_FOLDER"], "test_image.png"), "wb"
        ) as f:
            f.write(b"test image data")
        response = self.client.get("/uploads/test_image.png")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"test image data")

    @patch("src.web_app.app.TextExtractor")
    def test_process_file(self, mock_text_extractor):
        mock_text_extractor_instance = MagicMock()
        mock_text_extractor.return_value = mock_text_extractor_instance
        mock_text_extractor_instance.run.return_value = "Processed text"

        with open(
            os.path.join(self.app.config["UPLOAD_FOLDER"], "test_image.png"), "wb"
        ) as f:
            f.write(b"test image data")

        file_path = os.path.join(self.app.config["UPLOAD_FOLDER"], "test_image.png")
        self.assertTrue(os.path.exists(file_path))

        response = self.client.post("/process/test_image.png")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()

        print("")
        print(f"json_data: {json_data}")
        print("")

        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["result"], "Processed text")
        mock_text_extractor_instance.run.assert_called_once_with(file_path)

    def test_process_file_not_found(self):
        response = self.client.post("/process/non_existent_image.png")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertEqual(
            json_data["message"], "The image was not found, please reupload it."
        )


if __name__ == "__main__":
    unittest.main()

import cv2
import numpy as np
import unittest
from PIL import Image

from unittest.mock import patch, mock_open, MagicMock
from src.text_extractor.app import TextExtractor
from src.text_extractor.constants import Constants


class TestTextExtractor(unittest.TestCase):

    @patch("src.text_extractor.app.os.path.abspath")
    @patch("src.text_extractor.app.cv2.imread")
    def test_load_image(self, mock_imread, mock_abspath):
        mock_abspath.return_value = "fake/path/to/image.png"
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)

        extractor = TextExtractor()
        image = extractor.load_image("fake/path/to/image.png")

        mock_abspath.assert_called_once_with("fake/path/to/image.png")
        mock_imread.assert_called_once_with("fake/path/to/image.png", cv2.IMREAD_COLOR)
        self.assertIsNotNone(image)

    @patch("src.text_extractor.app.Image.open")
    @patch("src.text_extractor.app.tempfile.NamedTemporaryFile")
    def test_resize_image(self, mock_tempfile, mock_image_open):
        mock_img = MagicMock()
        mock_img.size = (100, 100)
        mock_img.resize.return_value = mock_img
        mock_image_open.return_value = mock_img

        mock_temp = MagicMock()
        mock_temp.name = "fake/temp/file.png"
        mock_tempfile.return_value = mock_temp

        extractor = TextExtractor()
        resized_image_path = extractor.resize_image("fake/path/to/image.png")

        self.assertEqual(resized_image_path, "fake/temp/file.png")
        mock_image_open.assert_called_once_with("fake/path/to/image.png")
        mock_img.resize.assert_called_once_with((200, 200), Image.Resampling.LANCZOS)
        mock_img.save.assert_called_once_with("fake/temp/file.png", dpi=(1200, 1200))

    @patch("src.text_extractor.app.TextExtractor.load_image")
    @patch("src.text_extractor.app.TextExtractor.resize_image")
    def test_pre_process_image(self, mock_resize_image, mock_load_image):
        mock_resize_image.return_value = "fake/resized/image.png"
        mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_load_image.return_value = mock_img

        extractor = TextExtractor()
        processed_image = extractor.pre_process_image("fake/path/to/image.png")

        self.assertIsNotNone(processed_image)
        mock_resize_image.assert_called_once_with("fake/path/to/image.png")
        mock_load_image.assert_called_once_with("fake/resized/image.png")

    @patch("src.text_extractor.app.cv2.findContours")
    @patch("src.text_extractor.app.imutils.grab_contours")
    def test_draw_contours_and_crop_images(
        self, mock_grab_contours, mock_find_contours
    ):
        mock_find_contours.return_value = ([], None)
        mock_grab_contours.return_value = [np.array([[0, 0], [0, 1], [1, 1], [1, 0]])]

        mock_img = np.zeros((100, 100), dtype=np.uint8)

        extractor = TextExtractor()
        cropped_images = extractor.draw_contours_and_crop_images(mock_img)

        self.assertEqual(len(cropped_images), 1)
        mock_find_contours.assert_called_once_with(
            mock_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        mock_grab_contours.assert_called_once()

    @patch("src.text_extractor.app.pytesseract.image_to_string")
    def test_apply_ocr(self, mock_image_to_string):
        mock_image_to_string.return_value = "Detected text"

        mock_image_data = {
            "image": np.zeros((100, 100), dtype=np.uint8),
            "segmentation": Constants.HORIZONTAL_SEGMENTATION_MODE,
        }

        extractor = TextExtractor()
        text_data = extractor.apply_ocr([mock_image_data])

        self.assertEqual(text_data, ["Detected text"])
        mock_image_to_string.assert_called_once_with(
            mock_image_data["image"],
            lang=Constants.JPN_LANGUAGE,
            config=f"{Constants.ENGINE_MODE} {Constants.HORIZONTAL_SEGMENTATION_MODE}",
        )

    def test_normalize_text(self):
        extractor = TextExtractor()
        normalized_text = extractor.normalize_text(
            ["   This  is   a test  ", "\n\nAnother   line"]
        )
        self.assertEqual(normalized_text, " This is a test \n Another line\n")

    @patch("src.text_extractor.app.open", new_callable=mock_open)
    @patch("src.text_extractor.app.os.path.abspath")
    def test_save_text_to_file(self, mock_abspath, mock_open_file):
        mock_abspath.return_value = "fake/path/to/output.txt"

        extractor = TextExtractor()
        extractor.save_text_to_file("Sample text")

        mock_abspath.assert_called_once_with(
            "./src/text_extractor/output/recognized.txt"
        )
        mock_open_file.assert_called_once_with("fake/path/to/output.txt", "w")
        mock_open_file().write.assert_called_once_with("Sample text")

    @patch("src.text_extractor.app.TextExtractor.pre_process_image")
    @patch("src.text_extractor.app.TextExtractor.draw_contours_and_crop_images")
    @patch("src.text_extractor.app.TextExtractor.apply_ocr")
    @patch("src.text_extractor.app.TextExtractor.normalize_text")
    @patch("src.text_extractor.app.TextExtractor.save_text_to_file")
    @patch("src.text_extractor.app.TextExtractor.display_images")
    def test_run(
        self,
        mock_display_images,
        mock_save_text_to_file,
        mock_normalize_text,
        mock_apply_ocr,
        mock_draw_contours,
        mock_pre_process,
    ):
        mock_pre_process.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_draw_contours.return_value = [
            {
                "image": np.zeros((100, 100), dtype=np.uint8),
                "segmentation": Constants.HORIZONTAL_SEGMENTATION_MODE,
            }
        ]
        mock_apply_ocr.return_value = ["Detected text"]
        mock_normalize_text.return_value = "Normalized text"

        extractor = TextExtractor(debug=True)
        result = extractor.run("fake/path/to/image.png")

        self.assertEqual(result, "Normalized text")
        mock_pre_process.assert_called_once_with("fake/path/to/image.png")
        mock_draw_contours.assert_called_once()
        mock_apply_ocr.assert_called_once()
        mock_normalize_text.assert_called_once_with(["Detected text"])
        mock_save_text_to_file.assert_called_once_with("Normalized text")
        mock_display_images.assert_called_once()

    @patch.object(TextExtractor, "pre_process_image")
    @patch("src.text_extractor.app.logger")
    def test_run_exception_handling(self, mock_logger, mock_pre_process_image):
        # Arrange
        mock_pre_process_image.side_effect = Exception("Test exception")
        text_extractor = TextExtractor()

        # Act
        result = text_extractor.run("dummy_input_file")

        # Assert
        self.assertFalse(result)
        mock_logger.error.assert_called()
        self.assertIn(
            "Error when running text extractor",
            mock_logger.error.call_args_list[0][0][0],
        )
        self.assertIn("Test exception", mock_logger.error.call_args_list[1][0][0])


if __name__ == "__main__":
    unittest.main()

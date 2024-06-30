import os
import re
import cv2
import traceback
import pytesseract
import numpy as np
import tempfile
import imutils
from PIL import Image

from src.logger import get_logger
from src.text_extractor.constants import Constants

logger = get_logger(__name__)


class TextExtractor:

    def __init__(
        self,
        language=Constants.JPN_LANGUAGE,
        vertical_language=Constants.JPN_VERT_LANGUAGE,
        engine_mode=Constants.ENGINE_MODE,
        save_text_in_file=True,
        debug=False,
    ):
        self.output_file_path = "./src/text_extractor/output/recognized.txt"
        self.language = language
        self.vertical_language = vertical_language
        self.engine_mode = engine_mode
        self.save_text_in_file = save_text_in_file
        self.debug = debug

    def load_image(self, input_file):
        absolute_path = os.path.abspath(input_file)
        image = cv2.imread(absolute_path, cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Image not found at {input_file}")
        return image

    def resize_image(self, image):
        img = Image.open(image)

        length_x, width_y = img.size
        new_size = (length_x * 2, width_y * 2)

        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_filename = temp_file.name

        img_resized.save(temp_filename, dpi=(1200, 1200))

        return temp_filename

    def pre_process_image(self, image):

        resized_img = self.resize_image(image)
        processed_image = self.load_image(resized_img)

        # Normalize the image
        img_shape = np.zeros((processed_image.shape[0], processed_image.shape[1]))
        processed_image = cv2.normalize(
            processed_image, img_shape, 0, 255, cv2.NORM_MINMAX
        )

        # Convert to grayscale
        processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

        # Apply Sharpeninng
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        processed_image = cv2.filter2D(processed_image, -1, kernel)

        # Apply Gaussian blur
        processed_image = cv2.GaussianBlur(processed_image, (7, 7), 0)

        # Apply Otsu thresholding
        processed_image = cv2.threshold(
            processed_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        return processed_image

    def draw_contours_and_crop_images(self, image):

        images = []
        min_area = 100
        min_aspect_ratio = 0.1

        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Check if the contour is valid
            if not w * h > min_area and not w / h > min_aspect_ratio:
                continue

            image_data = {
                "image": None,
                "segmentation": Constants.HORIZONTAL_SEGMENTATION_MODE,
            }

            # Check if the text is vertical
            if h > w:
                image_data["segmentation"] = Constants.VERTICAL_SEGMENTATION_MODE

            # draw contours and crop the image
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(image, (x, y), 8, (255, 255, 0), 8)
            cropped = image[y : y + h, x : x + w]
            image_data["image"] = cropped

            images.append(image_data)

        return images

    def apply_ocr(self, cropped_images):

        text_data = []

        for image in cropped_images:

            text = pytesseract.image_to_string(
                image["image"],
                lang=self.language,
                config=f"{self.engine_mode} {image['segmentation']}",
            )

            text_data.append(text)

        return text_data

    def normalize_text(self, text_data):
        normalized_text = ""
        for text in text_data:
            normalized_text += re.sub(r"\s+", " ", text) + "\n"
        return normalized_text

    def save_text_to_file(self, text):
        absolute_path = os.path.abspath(self.output_file_path)
        with open(absolute_path, "w") as file:
            file.write(text)

    def display_images(self, images):
        for window_name, image in images.items():
            resized_image = cv2.resize(image, (0, 0), fx=0.4, fy=0.4)
            cv2.imshow(window_name, resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run(self, input_file):

        try:
            pre_processed_img = self.pre_process_image(input_file)
            cropped_images = self.draw_contours_and_crop_images(pre_processed_img)
            text_data = self.apply_ocr(cropped_images)
            normalized_text = self.normalize_text(text_data)

            if self.save_text_in_file:
                self.save_text_to_file(normalized_text)

            if self.debug:
                images = {"Pre-processed Image": pre_processed_img}
                self.display_images(images)

            return normalized_text

        except Exception as e:
            logger.error(f"Error when running text extractor: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

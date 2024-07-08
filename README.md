# Japanese Image to Text Webapp

## Goal

The japanese-image-to-text-webapp is a production-ready web application crafted to extract Japanese text from images. Utilizing technologies such as OpenCV and Tesseract OCR.

Key features include:

- Advanced Image Processing: Leveraging OpenCV for preprocessing ensures optimal image quality for text detection.
- High-Precision OCR: Tesseract OCR is employed to achieve accurate text extraction.
- Seamless CI/CD Pipelines: Implemented Continuous Integration and Continuous Deployment through GitHub Actions workflows guarantee robust, reliable, and automated deployments.
- Containerization with Docker: The application is fully containerized, facilitating effortless deployment and scalability across various environments.

## Demo Video

[![Watch the demo video](https://github.com/nikholasborges/personal-image-host/blob/main/project%20thumb.png)](https://vimeo.com/manage/videos/980839427)


## Running Locally

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/nikholasborges/japanese-image-to-text-webapp.git
   cd japanese-image-to-text-webapp
   ```

2. **Install Dependencies:**
   Ensure Poetry is installed, then run:
   ```sh
   make install
   ```

4. **Run the Application:**
   ```sh
   make run
   ```

5. **Access the Application:**
   Open your web browser and go to `http://localhost:8000`.

## Building and Running as a Docker Container

1. **Build the Docker Image:**
   ```sh
   docker build -t japanese-image-to-text-webapp .
   ```

2. **Run the Docker Container:**
   ```sh
   docker run -d -p 8000:8000 japanese-image-to-text-webapp
   ```

3. **Access the Application:**
   Open your web browser and go to `http://localhost:8000`.

## GitHub Action Workflow Explanation

The GitHub Action workflow automates the CI/CD process for this project. It includes steps to:

- **Checkout the Code:** Retrieve the latest code from the repository.
- **Set Up Python:** Install Python 3.11.9.
- **Install Dependencies:** Use the `make install` command to install dependencies.
- **Create Directories:** Ensure necessary directories are created.
- **Lint Code:** Run `flake8` to check code quality.
- **Run Tests:** Execute tests using `pytest`.
- **Deploy to Docker Hub:** On pushes to the `main` branch, build and push the Docker image to Docker Hub using secrets for Docker credentials.

The workflow ensures code quality, runs tests, and deploys the image automatically.

## Future Goals

As the tool continues to evolve, Here's some of the future goals that's planned to be achieved in this project:

- **Enhanced OCR Options:** integrate more OCR options to improve Japanese text detection, ensuring even greater accuracy and versatility.
- **Improved Vertical Text Accuracy:** better train the Japanese-vert data, we aim to significantly enhance the accuracy of vertical text recognition.
- **Login Sessions:** work on adding a login session feature to keep your recently extracted texts and images in history, making it easier to track and revisit your work.
- **Character Cherry-Picking:** A new feature to allow users to cherry-pick specific characters from the extracted text, enabling quick and efficient lookups in dictionaries.

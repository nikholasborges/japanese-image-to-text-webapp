# Use the official Python image from the Docker Hub
FROM python:3.11-slim-bookworm 

# Set the working directory
WORKDIR /

# Copy the requirements file and the Makefile into the container
COPY pyproject.toml poetry.lock Makefile ./

# Ensure that all the dependencies are up to date
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y curl
RUN apt-get install -y 'ffmpeg'
RUN apt-get install -y 'libsm6'
RUN apt-get install -y 'libxext6'
RUN apt install libgl1-mesa-glx -y
RUN apt install tesseract-ocr -y
RUN apt install tesseract-ocr-jpn -y
RUN apt install tesseract-ocr-jpn-vert -y

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the application will run on
EXPOSE 8000

# Define the command to run the application using Makefile
CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:flask_app"]
# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /src

# Copy the requirements file and the Makefile into the container
COPY pyproject.toml poetry.lock Makefile ./

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
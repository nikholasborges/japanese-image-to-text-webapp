# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /

# Copy the requirements file and the Makefile into the container
COPY pyproject.toml Makefile ./

# Install Poetry
RUN pip install poetry

# Install dependencies using Makefile
RUN make install

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the application will run on
EXPOSE 8000

# Define the command to run the application using Makefile
CMD ["make", "run"]
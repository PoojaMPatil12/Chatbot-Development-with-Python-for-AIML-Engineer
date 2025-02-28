# Use the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the app files to the container
COPY . /app

# Install system dependencies for PyMuPDF
RUN apt-get update && \
    apt-get install -y libglib2.0-0 libfreetype6 libxext6 libsm6 libxrender1 && \
    apt-get clean

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn PyMuPDF ollama requests python-multipart

# Set the environment variable for Ollama URL
#ENV OLLAMA_URL=http://127.0.0.1:11434

# Expose the port the app runs on
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

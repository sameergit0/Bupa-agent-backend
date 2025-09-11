# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to the root of the application
WORKDIR /app

# Install system dependencies needed for SSL and others
RUN apt-get update && apt-get install -y openssl build-essential python3-tk

# Copy all application code and certificates into the container's working directory
# The `.` at the end means "copy all files from the local build context here"
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set permissions for the certificate files
RUN chmod 644 private-key.pem certificate.pem

# Expose the standard HTTPS/WSS port
EXPOSE 443

# Start the uvicorn server with SSL enabled
# Note: The server should now be able to find the files directly in the /app directory.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443", "--ws", "websockets", "--ssl-keyfile", "private-key.pem", "--ssl-certfile", "certificate.pem"]

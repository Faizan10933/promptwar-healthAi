# Use official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local code to the container
COPY . /app/

# Run the web service on container startup using gunicorn
# 1 worker, 8 threads as a balance
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

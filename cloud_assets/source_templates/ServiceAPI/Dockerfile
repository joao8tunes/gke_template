# Use the official lightweight Python image (https://hub.docker.com/_/python).
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy local code to the container image.
COPY . ./

# Install app dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Run the web service on container startup. Here we use the gunicorn webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers to be equal to the cores available.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "wsgi:app"]

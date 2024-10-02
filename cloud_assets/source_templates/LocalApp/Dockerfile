# Use the official lightweight Python image (https://hub.docker.com/_/python)
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy local code to the container image
COPY . ./

# Install app dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Run the script when the container starts
CMD ["python", "run.py"]

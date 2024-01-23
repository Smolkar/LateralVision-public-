# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN python3.9 -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel
RUN python3.9 -m pip install --no-cache-dir \
    -r requirements.txt
    

COPY . .

# Run the main.py file
CMD ["python", "main.py"]
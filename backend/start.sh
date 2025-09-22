#!/bin/bash

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
while ! nc -z resume_analyzer_mongodb 27017; do
  sleep 1
done
echo "MongoDB is ready!"

# Initialize the database
echo "Initializing database..."
python scripts/init_db.py

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000

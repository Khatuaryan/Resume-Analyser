#!/bin/bash

# Initialize Firebase connection and data
echo "🔥 Initializing Firebase connection and data..."
python scripts/setup_firebase.py
echo "✅ Firebase setup completed"

# Start the FastAPI application
echo "🚀 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
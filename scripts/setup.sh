#!/bin/bash

# Smart Resume Analyzer Platform Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Smart Resume Analyzer Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads/resumes
mkdir -p data
mkdir -p nginx/ssl

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp env.example .env
    echo "✅ Environment file created. Please review and update .env file with your settings."
fi

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Create sample data
echo "📊 Creating sample data..."
cd data
python3 example_data.py
cd ..

echo "✅ Setup completed successfully!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "👤 Sample users:"
echo "   HR: hr@techcorp.com / password123"
echo "   Candidate 1: candidate1@email.com / password123"
echo "   Candidate 2: candidate2@email.com / password123"
echo ""
echo "📝 To stop the services: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"
echo "📝 To restart: docker-compose restart"

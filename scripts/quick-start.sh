#!/bin/bash

# Smart Resume Analyzer Platform - Quick Start Script
# This script automates the setup process from scratch

set -e  # Exit on any error

echo "🚀 Smart Resume Analyzer Platform - Quick Start"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop first."
        echo "Download from: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Desktop first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Docker is running
check_docker_running() {
    print_status "Checking if Docker is running..."
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    print_success "Docker is running"
}

# Create environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_success "Created .env file from env.example"
        else
            print_warning "env.example not found, creating basic .env file"
            cat > .env << EOF
# Database Configuration
MONGODB_URL=mongodb://admin:password123@mongodb:27017/resume_analyzer?authSource=admin
DATABASE_NAME=resume_analyzer

# Authentication
SECRET_KEY=your-super-secret-key-change-in-production-12345
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis
REDIS_URL=redis://redis:6379

# Feature Toggles
ENABLE_ML_MODELS=true
ENABLE_LLM=false
ENABLE_OCR=true
ENABLE_MULTILINGUAL=true
ENABLE_ONTOLOGY=true
ENABLE_BIAS_DETECTION=true

# LLM Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
EOF
        fi
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p uploads/temp
    mkdir -p data
    mkdir -p logs
    mkdir -p models
    
    print_success "Created necessary directories"
}

# Set up permissions
setup_permissions() {
    print_status "Setting up permissions..."
    
    # Make scripts executable
    chmod +x scripts/*.sh 2>/dev/null || true
    
    # Set proper permissions for uploads
    chmod 755 uploads
    chmod 755 uploads/temp
    
    print_success "Set up permissions"
}

# Choose architecture
choose_architecture() {
    echo ""
    print_status "Choose your architecture:"
    echo "1) Monolithic (Recommended for beginners)"
    echo "2) Microservices (Advanced users)"
    echo ""
    read -p "Enter your choice (1 or 2): " choice
    
    case $choice in
        1)
            ARCHITECTURE="monolithic"
            COMPOSE_FILE="docker-compose.yml"
            print_success "Selected Monolithic architecture"
            ;;
        2)
            ARCHITECTURE="microservices"
            COMPOSE_FILE="docker-compose.microservices.yml"
            print_success "Selected Microservices architecture"
            ;;
        *)
            print_warning "Invalid choice, defaulting to Monolithic"
            ARCHITECTURE="monolithic"
            COMPOSE_FILE="docker-compose.yml"
            ;;
    esac
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Stop any existing containers
    docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
    
    # Build and start services
    docker-compose -f $COMPOSE_FILE up -d --build
    
    print_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend to be ready
    print_status "Waiting for backend service..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend service is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "Backend service took longer than expected to start"
    fi
    
    # Wait for frontend to be ready
    print_status "Waiting for frontend service..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            print_success "Frontend service is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "Frontend service took longer than expected to start"
    fi
}

# Check service health
check_services() {
    print_status "Checking service health..."
    
    # Check backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend API is healthy"
    else
        print_error "Backend API is not responding"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend is not accessible"
    fi
    
    # Check database
    if docker-compose -f $COMPOSE_FILE exec -T mongodb mongosh --eval "db.runCommand('ping')" >/dev/null 2>&1; then
        print_success "Database is healthy"
    else
        print_warning "Database health check failed"
    fi
}

# Display access information
display_access_info() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    print_success "Your Smart Resume Analyzer Platform is now running!"
    echo ""
    echo "📱 Access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo ""
    echo "👤 Default User Accounts:"
    echo "  HR User: hr@techcorp.com / password123"
    echo "  Candidate: candidate1@email.com / password123"
    echo "  Candidate: candidate2@email.com / password123"
    echo ""
    echo "🔧 Management Commands:"
    echo "  View logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "  Restart services: docker-compose -f $COMPOSE_FILE restart"
    echo ""
    echo "📚 Documentation:"
    echo "  Complete Setup Guide: COMPLETE_SETUP_GUIDE.md"
    echo "  Advanced Features: ADVANCED_FEATURES_GUIDE.md"
    echo "  README: README.md"
    echo ""
}

# Main execution
main() {
    echo "Starting Smart Resume Analyzer Platform setup..."
    echo ""
    
    # Run setup steps
    check_docker
    check_docker_running
    setup_environment
    create_directories
    setup_permissions
    choose_architecture
    start_services
    wait_for_services
    check_services
    display_access_info
    
    echo ""
    print_success "Setup completed successfully! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Login with the provided credentials"
    echo "3. Start using the platform!"
    echo ""
}

# Run main function
main "$@"

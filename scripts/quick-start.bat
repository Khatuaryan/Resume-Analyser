@echo off
REM Smart Resume Analyzer Platform - Quick Start Script for Windows
REM This script automates the setup process from scratch

echo 🚀 Smart Resume Analyzer Platform - Quick Start
echo ==============================================

REM Check if Docker is installed
echo [INFO] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo [SUCCESS] Docker and Docker Compose are installed

REM Check if Docker is running
echo [INFO] Checking if Docker is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is running

REM Create environment file
echo [INFO] Setting up environment configuration...
if not exist .env (
    if exist env.example (
        copy env.example .env >nul
        echo [SUCCESS] Created .env file from env.example
    ) else (
        echo [WARNING] env.example not found, creating basic .env file
        (
            echo # Database Configuration
            echo MONGODB_URL=mongodb://admin:password123@mongodb:27017/resume_analyzer?authSource=admin
            echo DATABASE_NAME=resume_analyzer
            echo.
            echo # Authentication
            echo SECRET_KEY=your-super-secret-key-change-in-production-12345
            echo ACCESS_TOKEN_EXPIRE_MINUTES=1440
            echo.
            echo # Redis
            echo REDIS_URL=redis://redis:6379
            echo.
            echo # Feature Toggles
            echo ENABLE_ML_MODELS=true
            echo ENABLE_LLM=false
            echo ENABLE_OCR=true
            echo ENABLE_MULTILINGUAL=true
            echo ENABLE_ONTOLOGY=true
            echo ENABLE_BIAS_DETECTION=true
            echo.
            echo # LLM Configuration (Optional)
            echo OPENAI_API_KEY=your-openai-api-key-here
            echo ANTHROPIC_API_KEY=your-anthropic-api-key-here
            echo LLM_PROVIDER=openai
            echo LLM_MODEL=gpt-3.5-turbo
        ) > .env
    )
) else (
    echo [WARNING] .env file already exists, skipping creation
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist uploads mkdir uploads
if not exist uploads\temp mkdir uploads\temp
if not exist data mkdir data
if not exist logs mkdir logs
if not exist models mkdir models
echo [SUCCESS] Created necessary directories

REM Choose architecture
echo.
echo [INFO] Choose your architecture:
echo 1) Monolithic (Recommended for beginners)
echo 2) Microservices (Advanced users)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    set ARCHITECTURE=monolithic
    set COMPOSE_FILE=docker-compose.yml
    echo [SUCCESS] Selected Monolithic architecture
) else if "%choice%"=="2" (
    set ARCHITECTURE=microservices
    set COMPOSE_FILE=docker-compose.microservices.yml
    echo [SUCCESS] Selected Microservices architecture
) else (
    echo [WARNING] Invalid choice, defaulting to Monolithic
    set ARCHITECTURE=monolithic
    set COMPOSE_FILE=docker-compose.yml
)

REM Build and start services
echo [INFO] Building and starting services...
docker-compose -f %COMPOSE_FILE% down >nul 2>&1
docker-compose -f %COMPOSE_FILE% up -d --build
echo [SUCCESS] Services started successfully

REM Wait for services
echo [INFO] Waiting for services to be ready...
echo [INFO] This may take a few minutes...

REM Wait for backend
timeout /t 30 /nobreak >nul
echo [INFO] Checking backend service...
:check_backend
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Backend not ready yet, waiting...
    timeout /t 5 /nobreak >nul
    goto check_backend
)
echo [SUCCESS] Backend service is ready

REM Wait for frontend
echo [INFO] Checking frontend service...
:check_frontend
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Frontend not ready yet, waiting...
    timeout /t 5 /nobreak >nul
    goto check_frontend
)
echo [SUCCESS] Frontend service is ready

REM Display access information
echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo [SUCCESS] Your Smart Resume Analyzer Platform is now running!
echo.
echo 📱 Access URLs:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Documentation: http://localhost:8000/docs
echo.
echo 👤 Default User Accounts:
echo   HR User: hr@techcorp.com / password123
echo   Candidate: candidate1@email.com / password123
echo   Candidate: candidate2@email.com / password123
echo.
echo 🔧 Management Commands:
echo   View logs: docker-compose -f %COMPOSE_FILE% logs -f
echo   Stop services: docker-compose -f %COMPOSE_FILE% down
echo   Restart services: docker-compose -f %COMPOSE_FILE% restart
echo.
echo 📚 Documentation:
echo   Complete Setup Guide: COMPLETE_SETUP_GUIDE.md
echo   Advanced Features: ADVANCED_FEATURES_GUIDE.md
echo   README: README.md
echo.

echo [SUCCESS] Setup completed successfully! 🎉
echo.
echo Next steps:
echo 1. Open http://localhost:3000 in your browser
echo 2. Login with the provided credentials
echo 3. Start using the platform!
echo.
pause

# 🚀 Complete Setup Guide - Smart Resume Analyzer Platform

This guide will take you from zero to a fully running Smart Resume Analyzer Platform with all advanced features.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 10GB free space
- **CPU**: 4 cores minimum (8 cores recommended)

### Required Software
1. **Docker Desktop** (Latest version)
2. **Git** (Latest version)
3. **Node.js** (v18 or higher)
4. **Python** (v3.11 or higher) - for local development

## 🔧 Step 1: Install Prerequisites

### Install Docker Desktop
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop
3. Verify installation:
```bash
docker --version
docker-compose --version
```

### Install Git
1. Download Git from [git-scm.com](https://git-scm.com/)
2. Install with default settings
3. Verify installation:
```bash
git --version
```

### Install Node.js (Optional - for local development)
1. Download Node.js 18.20.4 LTS from [nodejs.org](https://nodejs.org/)
2. Install the LTS version (18.20.4)
3. Verify installation:
```bash
node --version  # Should show v18.20.4
npm --version   # Should show 10.2.4
```

**Recommended Node.js Version: 18.20.4 LTS**
- Most stable for React 18.x projects
- Excellent Docker support
- Long-term support until April 2025
- Perfect compatibility with all project dependencies

## 📥 Step 2: Clone and Setup Project

### Clone the Repository
```bash
# Navigate to your desired directory
cd /path/to/your/projects

# Clone the repository
git clone <your-repository-url>
cd "Smart Resume Analyzer Platform"
```

### Alternative: Download and Extract
If you have the project files locally, navigate to the project directory:
```bash
cd "/Users/khatuaryan/Desktop/Aryan/Studies/SEM VII/NLP/Major Project"
```

## ⚙️ Step 3: Environment Configuration

### Create Environment File
```bash
# Copy the example environment file
cp env.example .env
```

### Edit Environment Variables
Open `.env` file and configure:

```bash
# Database Configuration
MONGODB_URL=mongodb://admin:password123@mongodb:27017/resume_analyzer?authSource=admin
DATABASE_NAME=resume_analyzer

# Authentication
SECRET_KEY=your-super-secret-key-change-in-production-12345
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis (for microservices)
REDIS_URL=redis://redis:6379

# Feature Toggles (Enable/Disable Advanced Features)
ENABLE_ML_MODELS=true
ENABLE_LLM=false
ENABLE_OCR=true
ENABLE_MULTILINGUAL=true
ENABLE_ONTOLOGY=true
ENABLE_BIAS_DETECTION=true

# LLM Configuration (Optional - only if ENABLE_LLM=true)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Service URLs (for microservices)
ML_SERVICE_URL=http://localhost:8001
OCR_SERVICE_URL=http://localhost:8002
LLM_SERVICE_URL=http://localhost:8003
ONTOLOGY_SERVICE_URL=http://localhost:8004
BIAS_SERVICE_URL=http://localhost:8005
```

## 🐳 Step 4: Choose Architecture

### Option A: Monolithic Architecture (Recommended for Beginners)
```bash
# Use the standard docker-compose.yml
# This runs everything in a single container
```

### Option B: Microservices Architecture (Advanced)
```bash
# Use docker-compose.microservices.yml
# This separates services into individual containers
```

## 🚀 Step 5: Start the Application

### For Monolithic Architecture (Recommended)
```bash
# Start all services
docker-compose up -d

# Check if all services are running
docker-compose ps
```

### For Microservices Architecture
```bash
# Start microservices
docker-compose -f docker-compose.microservices.yml up -d

# Check if all services are running
docker-compose -f docker-compose.microservices.yml ps
```

### Monitor Startup
```bash
# View logs to ensure everything starts correctly
docker-compose logs -f

# Or for microservices
docker-compose -f docker-compose.microservices.yml logs -f
```

## 🔍 Step 6: Verify Installation

### Check Service Health
```bash
# Check if all services are running
curl http://localhost:8000/health
curl http://localhost:3000
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 👤 Step 7: Create User Accounts

### Access the Application
1. Open your browser and go to http://localhost:3000
2. You should see the login page

### Register New Users
1. Click "Register" or "Sign Up"
2. Create accounts for different user types:

#### HR User Account
```
Email: hr@techcorp.com
Password: password123
Role: HR
```

#### Candidate User Account
```
Email: candidate1@email.com
Password: password123
Role: Candidate
```

### Alternative: Use Pre-created Accounts
The system comes with example data including:
- HR users
- Candidate users
- Sample jobs
- Sample resumes

## 📊 Step 8: Test Core Features

### For HR Users
1. **Login** with HR credentials
2. **Post a Job**:
   - Go to "Post Job"
   - Fill in job details
   - Add required skills
   - Submit job posting

3. **View Candidates**:
   - Go to "Candidates" tab
   - View candidate rankings
   - Analyze candidate profiles

4. **Bias Dashboard** (if enabled):
   - Go to "Bias Dashboard"
   - View bias detection reports
   - Review bias mitigation recommendations

### For Candidate Users
1. **Login** with candidate credentials
2. **Upload Resume**:
   - Go to "Upload Resume"
   - Upload PDF/DOCX file
   - Wait for processing

3. **View Jobs**:
   - Go to "Jobs" tab
   - Browse available jobs
   - Apply to relevant positions

4. **Skill Suggestions**:
   - Go to "Skill Suggestions"
   - View personalized recommendations
   - See skill gap analysis

## 🔧 Step 9: Configure Advanced Features

### Enable ML Models (Already enabled by default)
```bash
# ML models are automatically trained with example data
# No additional configuration needed
```

### Enable OCR Processing (Already enabled by default)
```bash
# OCR is automatically available
# Test with image-based resumes
```

### Enable Multilingual Support (Already enabled by default)
```bash
# Supports English, Spanish, French, German, Italian, Portuguese
# Automatic language detection
```

### Enable LLM Integration (Optional)
1. Get API keys from OpenAI or Anthropic
2. Update `.env` file:
```bash
ENABLE_LLM=true
OPENAI_API_KEY=your-actual-api-key
```
3. Restart services:
```bash
docker-compose restart backend
```

## 📈 Step 10: Monitor and Maintain

### View Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Service Status
```bash
# Check running containers
docker-compose ps

# Check resource usage
docker stats
```

### Backup Data
```bash
# Backup MongoDB data
docker-compose exec mongodb mongodump --out /backup
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

#### 2. Docker Not Running
```bash
# Start Docker Desktop
# On macOS: Open Docker Desktop app
# On Windows: Start Docker Desktop
# On Linux: sudo systemctl start docker
```

#### 3. Services Not Starting
```bash
# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

#### 4. Database Connection Issues
```bash
# Check MongoDB container
docker-compose logs mongodb

# Restart database
docker-compose restart mongodb
```

#### 5. Frontend Not Loading
```bash
# Check if frontend container is running
docker-compose ps frontend

# Restart frontend
docker-compose restart frontend
```

### Reset Everything
```bash
# Stop all services
docker-compose down

# Remove all containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## 🎯 Step 11: Production Deployment

### For Production Use
1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY**
3. **Enable HTTPS** in Nginx configuration
4. **Set up proper monitoring**
5. **Configure backups**

### Environment Variables for Production
```bash
# Production database
MONGODB_URL=mongodb://username:password@your-mongodb-host:27017/resume_analyzer

# Strong secret key
SECRET_KEY=your-very-strong-secret-key-for-production

# Production API keys
OPENAI_API_KEY=your-production-openai-key
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

### Support
- Check the `README.md` file for detailed information
- Review `ADVANCED_FEATURES_GUIDE.md` for advanced features
- Check logs for error messages
- Verify all prerequisites are installed

## ✅ Success Checklist

- [ ] Docker Desktop installed and running
- [ ] Project cloned/downloaded
- [ ] Environment variables configured
- [ ] Services started successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API accessible at http://localhost:8000
- [ ] User accounts created
- [ ] Resume upload working
- [ ] Job posting working
- [ ] Candidate ranking working
- [ ] Advanced features enabled (optional)

## 🎉 Congratulations!

You now have a fully functional Smart Resume Analyzer Platform with:
- ✅ User authentication and authorization
- ✅ Resume parsing and analysis
- ✅ Candidate ranking and scoring
- ✅ Job posting and management
- ✅ Skill recommendations
- ✅ Bias detection and auditing
- ✅ OCR and multilingual support
- ✅ ML models and LLM integration
- ✅ Microservices architecture (optional)

The platform is ready for use and can be customized further based on your specific needs!

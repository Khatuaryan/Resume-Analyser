# 🚀 Smart Resume Analyzer Platform

A comprehensive AI-powered resume analysis platform that helps HR professionals and candidates optimize the hiring process through intelligent resume parsing, candidate ranking, and bias detection.

## ✨ Features

### 🔐 **Authentication & User Management**
- **Dual Role System**: HR professionals and candidates
- **Secure JWT Authentication**: Persistent login sessions
- **Admin Panel**: System administration with persistent admin login
- **User Profiles**: Comprehensive user management

### 📄 **Resume Processing**
- **Multi-format Support**: PDF, DOCX, TXT files
- **OCR Processing**: Image-based resume parsing with Tesseract
- **Multilingual Support**: English, Spanish, French, German, Italian, Portuguese
- **Smart Parsing**: NLP-powered text extraction and analysis

### 🤖 **AI & Machine Learning**
- **Traditional ML Models**: Random Forest, KNN, Decision Tree
- **LLM Integration**: GPT-3.5/4 and Claude for contextual analysis
- **Knowledge Graph**: Semantic skill matching and ontology
- **Bias Detection**: Ethical AI auditing and bias mitigation

### 📊 **Candidate Management**
- **Intelligent Ranking**: Multi-algorithm candidate scoring
- **Skill Gap Analysis**: Personalized skill recommendations
- **Bias Dashboard**: Fair hiring practices monitoring
- **Enhanced Analytics**: Comprehensive candidate insights

### 🏢 **Job Management**
- **Job Posting**: Create and manage job listings
- **Application Tracking**: Monitor candidate applications
- **Skill Matching**: Automatic skill-job matching
- **Analytics Dashboard**: Job performance metrics

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** (Latest version)
- **Git** (Optional)
- **8GB RAM** (Recommended)
- **10GB Storage** (Minimum)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Resume-Analyser
```

### 2. Start the Platform
```bash
# For macOS/Linux
./scripts/quick-start.sh

# For Windows
scripts\quick-start.bat

# Or manually
docker-compose up -d
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 👤 Login Credentials

### Admin User (System Administrator)
```
Email: admin@resumeanalyzer.com
Password: password123@
Role: HR (Full Access)
```

### HR User (Post jobs, manage candidates)
```
Email: hr@techcorp.com
Password: password123
Role: HR
```

### Candidate User (Upload resume, apply jobs)
```
Email: candidate1@email.com
Password: password123
Role: Candidate
```

## 🏗️ Architecture Options

### Monolithic Architecture (Default)
```bash
docker-compose up -d
```
- **Single container** deployment
- **Easy management** and development
- **Lower resource usage**
- **Perfect for development** and small teams

### Microservices Architecture (Advanced)
```bash
docker-compose -f docker-compose.microservices.yml up -d
```
- **Distributed services** for scalability
- **Independent scaling** of components
- **Better fault isolation**
- **Production-ready** architecture

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Database Configuration
MONGODB_URL=mongodb://admin:password123@mongodb:27017/resume_analyzer?authSource=admin
DATABASE_NAME=resume_analyzer

# Authentication
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Feature Toggles
ENABLE_ML_MODELS=true
ENABLE_LLM=false
ENABLE_OCR=true
ENABLE_MULTILINGUAL=true
ENABLE_ONTOLOGY=true
ENABLE_BIAS_DETECTION=true

# LLM Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

## 🎯 Core Workflows

### For HR Professionals
1. **Login** with HR credentials
2. **Post Jobs** with detailed requirements
3. **View Candidates** with intelligent rankings
4. **Analyze Bias** using the bias dashboard
5. **Manage Applications** and track progress

### For Candidates
1. **Login** with candidate credentials
2. **Upload Resume** (PDF, DOCX, TXT)
3. **Browse Jobs** and apply to positions
4. **View Skill Suggestions** for improvement
5. **Track Applications** and status

## 🔬 Advanced Features

### 1. Traditional ML Models
- **Random Forest** regression for scoring
- **K-Nearest Neighbors** for similarity
- **Decision Tree** models for classification
- **Ensemble scoring** for accuracy

### 2. LLM Integration
- **GPT-3.5/4** for contextual analysis
- **Claude** integration for advanced reasoning
- **Contextual feedback** for candidates
- **Bias detection** and mitigation

### 3. OCR & Multi-Modal Processing
- **Tesseract OCR** for image processing
- **EasyOCR** integration for accuracy
- **Multi-language OCR** support
- **Image preprocessing** and enhancement

### 4. Multilingual Support
- **Language Detection**: Automatic language identification
- **Multi-language NER**: Named entity recognition
- **Translation Support**: Cross-language analysis
- **Language-specific Parsing**: Optimized for each language

### 5. Knowledge Graph & Ontology
- **Skill Ontology**: Comprehensive skill taxonomy
- **Semantic Matching**: Intelligent skill relationships
- **Learning Paths**: Personalized skill development
- **Skill Relationships**: Understanding skill dependencies

### 6. Bias Detection & Ethical AI
- **Gender Bias Detection**: Fair gender representation
- **Name-based Bias**: Unconscious bias prevention
- **Education Bias**: Equal opportunity analysis
- **Geographic Bias**: Location-based fairness
- **Bias Reporting**: Comprehensive bias analytics

## 📊 API Endpoints

### Authentication
```bash
POST /auth/login          # User login
POST /auth/register       # User registration
GET  /auth/me            # Current user profile
```

### Resume Management
```bash
POST /resumes/upload      # Upload resume
GET  /resumes/           # List resumes
GET  /resumes/{id}       # Get resume details
POST /resumes/parse      # Parse resume content
```

### Job Management
```bash
POST /jobs/              # Create job
GET  /jobs/              # List jobs
GET  /jobs/{id}          # Get job details
PUT  /jobs/{id}          # Update job
DELETE /jobs/{id}        # Delete job
```

### Candidate Management
```bash
GET  /candidates/        # List candidates
GET  /candidates/{id}   # Get candidate details
POST /candidates/rank    # Rank candidates
GET  /candidates/analytics # Candidate analytics
```

### Advanced Features
```bash
GET  /advanced/capabilities     # Service capabilities
POST /advanced/ml-models/train  # Train ML models
GET  /advanced/bias/report     # Bias analysis report
POST /advanced/ocr/process     # OCR processing
```

## 🛠️ Management Commands

### Service Management
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Reset everything
docker-compose down -v
docker-compose up -d --build
```

### Database Management
```bash
# Backup database
docker-compose exec mongodb mongodump --out /backup

# Restore database
docker-compose exec mongodb mongorestore /backup

# Access MongoDB shell
docker exec -it resume_analyzer_mongodb mongosh
```

## 🔍 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker is running
docker info

# Check logs for errors
docker-compose logs

# Restart services
docker-compose restart
```

#### Port Conflicts
```bash
# Check what's using ports
lsof -i :3000
lsof -i :8000

# Kill processes or change ports in docker-compose.yml
```

#### Database Issues
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Restart database
docker-compose restart mongodb
```

#### Admin Login Issues
```bash
# Verify admin user exists
docker exec -it resume_analyzer_mongodb mongosh --eval "
  use resume_analyzer;
  db.users.findOne({email: 'admin@resumeanalyzer.com'});
"

# Test admin login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@resumeanalyzer.com", "password": "password123@"}'
```

### Performance Optimization

#### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 10GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 50GB storage
- **Production**: 16GB RAM, 8 CPU cores, 100GB storage

#### Scaling Guidelines
- **ML Models**: Scale based on training data size
- **OCR**: Scale based on image processing volume
- **LLM**: Scale based on API rate limits
- **Ontology**: Scale based on knowledge graph size

## 🔒 Security Considerations

### Production Deployment
1. **Change default passwords** in environment variables
2. **Use strong SECRET_KEY** for JWT tokens
3. **Enable HTTPS** in Nginx configuration
4. **Set up proper monitoring** and logging
5. **Configure regular backups**

### API Security
- **Rate limiting** for API endpoints
- **CORS configuration** for production
- **Input validation** for file uploads
- **Secure file storage** for resumes

## 📈 Monitoring & Analytics

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Service capabilities
curl http://localhost:8000/advanced/capabilities

# Bias dashboard
curl http://localhost:8000/advanced/bias/dashboard
```

### Logs and Debugging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

## 🎯 Success Indicators

### ✅ Platform Ready
- [ ] Frontend loads at http://localhost:3000
- [ ] Login page appears correctly
- [ ] Can login with admin credentials
- [ ] Can upload resume (candidate)
- [ ] Can post job (HR)
- [ ] Can view candidate rankings (HR)
- [ ] Bias dashboard accessible (HR)

### ✅ Advanced Features Working
- [ ] ML models training successfully
- [ ] OCR processing resumes
- [ ] Multilingual support active
- [ ] Bias detection functioning
- [ ] LLM integration working (if configured)

## 🚀 Next Steps

1. **Explore the platform** with provided accounts
2. **Upload test resumes** to see parsing in action
3. **Post sample jobs** to test the workflow
4. **Enable advanced features** by configuring API keys
5. **Customize** the platform for your needs
6. **Deploy to production** with proper security measures

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

### Support
- Check logs for error messages
- Verify all prerequisites are installed
- Review environment configuration
- Test with provided sample data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 You're all set! The Smart Resume Analyzer Platform is ready to revolutionize your hiring process!**
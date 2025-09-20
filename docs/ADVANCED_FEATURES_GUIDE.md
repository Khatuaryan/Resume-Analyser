# Advanced Features Integration Guide

This guide explains how to enable, configure, and use the advanced features in the Smart Resume Analyzer Platform.

## 🚀 Advanced Features Overview

The platform now includes the following advanced features:

1. **Traditional ML Models Fallback** - Random Forest, KNN, Decision Tree models
2. **LLM Integration** - GPT/Claude for contextual analysis
3. **OCR & Multi-Modal Parsing** - Image-based resume processing
4. **Multilingual Support** - Spanish, French, and other languages
5. **Knowledge Graph/Ontology** - Semantic skill matching
6. **Ethical AI & Bias Detection** - Bias auditing and mitigation
7. **Microservice Architecture** - Scalable service separation

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Database
MONGODB_URL=mongodb://admin:password123@localhost:27017/resume_analyzer?authSource=admin
DATABASE_NAME=resume_analyzer

# Authentication
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis (for microservices)
REDIS_URL=redis://localhost:6379

# Feature Toggles
ENABLE_ML_MODELS=true
ENABLE_LLM=false
ENABLE_OCR=true
ENABLE_MULTILINGUAL=true
ENABLE_ONTOLOGY=true
ENABLE_BIAS_DETECTION=true

# LLM Configuration (if ENABLE_LLM=true)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
LLM_PROVIDER=openai  # or anthropic
LLM_MODEL=gpt-3.5-turbo

# Service URLs (for microservices)
ML_SERVICE_URL=http://localhost:8001
OCR_SERVICE_URL=http://localhost:8002
LLM_SERVICE_URL=http://localhost:8003
ONTOLOGY_SERVICE_URL=http://localhost:8004
BIAS_SERVICE_URL=http://localhost:8005
```

## 🏗️ Architecture Options

### Option 1: Monolithic Architecture (Default)

Use the standard `docker-compose.yml` for a single-container setup:

```bash
# Start all services in one container
docker-compose up -d
```

**Pros:**
- Simple deployment
- Easy development
- Lower resource usage

**Cons:**
- Less scalable
- Single point of failure
- Harder to scale individual components

### Option 2: Microservices Architecture

Use `docker-compose.microservices.yml` for distributed services:

```bash
# Start microservices architecture
docker-compose -f docker-compose.microservices.yml up -d
```

**Pros:**
- Highly scalable
- Independent service scaling
- Better fault isolation
- Technology diversity

**Cons:**
- More complex deployment
- Higher resource usage
- Network latency between services

## 🔌 Feature Integration

### 1. Traditional ML Models

**Enable:** Set `ENABLE_ML_MODELS=true`

**Features:**
- Random Forest regression
- K-Nearest Neighbors
- Decision Tree models
- Ensemble scoring
- Model persistence

**API Endpoints:**
```bash
POST /api/advanced/ml-models/train
GET /api/advanced/capabilities
```

**Usage:**
```python
# Train models with historical data
training_data = [
    {
        "skills_count": 10,
        "experience_years": 5,
        "education_level": "bachelor",
        "skill_match_score": 85,
        "overall_score": 90
    }
]
response = await train_ml_models(training_data)
```

### 2. LLM Integration

**Enable:** Set `ENABLE_LLM=true` and provide API keys

**Features:**
- GPT-3.5/4 analysis
- Claude integration
- Contextual candidate feedback
- Skill recommendations
- Bias detection

**API Endpoints:**
```bash
GET /api/advanced/llm/analysis
POST /api/advanced/candidates/score-enhanced
```

**Usage:**
```python
# Analyze resume with LLM
llm_analysis = await analyze_resume_with_llm(resume_data, job_requirements)
```

### 3. OCR & Multi-Modal Parsing

**Enable:** Set `ENABLE_OCR=true`

**Features:**
- Tesseract OCR
- EasyOCR integration
- PDF to image conversion
- Multi-language OCR
- Image preprocessing

**API Endpoints:**
```bash
POST /api/advanced/ocr/process-image
POST /api/advanced/resumes/parse-enhanced
```

**Usage:**
```python
# Process image-based resume
ocr_result = await parse_image_resume("resume.pdf", "pdf", "en")
```

### 4. Multilingual Support

**Enable:** Set `ENABLE_MULTILINGUAL=true`

**Features:**
- Language detection
- Multi-language NER
- Translation support
- Language-specific parsing

**Supported Languages:**
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)

**API Endpoints:**
```bash
GET /api/advanced/multilingual/supported-languages
POST /api/advanced/resumes/parse-enhanced
```

### 5. Knowledge Graph/Ontology

**Enable:** Set `ENABLE_ONTOLOGY=true`

**Features:**
- Skill ontology
- Semantic matching
- Learning path recommendations
- Skill relationship mapping

**API Endpoints:**
```bash
GET /api/advanced/ontology/stats
POST /api/advanced/candidates/score-enhanced
```

### 6. Bias Detection

**Enable:** Set `ENABLE_BIAS_DETECTION=true`

**Features:**
- Gender bias detection
- Name-based bias
- Education bias
- Geographic bias
- Bias reporting

**API Endpoints:**
```bash
GET /api/advanced/bias/report
GET /api/advanced/bias/dashboard
POST /api/advanced/candidates/bias-analysis
```

## 🎯 Usage Examples

### Enhanced Resume Parsing

```python
# Parse resume with all advanced features
result = await parse_resume_enhanced(
    file_path="resume.pdf",
    file_type="pdf",
    language="en"
)

# Features used: OCR, Multilingual, LLM, Ontology
print(result['features_used'])
```

### Enhanced Candidate Scoring

```python
# Calculate score with all methods
score_result = await calculate_enhanced_candidate_score(
    resume_data=candidate_data,
    job_requirements=job_requirements
)

# Get individual scores
print(f"Base NLP: {score_result['individual_scores']['base_nlp']['overall_score']}")
print(f"ML Models: {score_result['individual_scores']['ml_models']['overall_score']}")
print(f"Ontology: {score_result['individual_scores']['ontology']['ontology_score']}")
```

### Bias Analysis

```python
# Analyze candidate for bias
bias_result = await analyze_candidate_bias(
    candidate_data=candidate_data,
    ranking_score=85.5,
    job_requirements=job_requirements
)

if bias_result['bias_detected']:
    print("Bias indicators detected:")
    for bias_type, indicator in bias_result['bias_indicators'].items():
        print(f"- {bias_type}: {indicator['confidence']:.2%} confidence")
```

## 📊 Monitoring and Analytics

### Service Health Checks

```bash
# Check all services
curl http://localhost/health/backend
curl http://localhost/health/ml
curl http://localhost/health/ocr
curl http://localhost/health/llm
curl http://localhost/health/ontology
curl http://localhost/health/bias
```

### Bias Dashboard

Access the bias detection dashboard at:
```
http://localhost:3000/bias-dashboard
```

### Service Capabilities

```bash
# Get all service capabilities
curl http://localhost:8000/api/advanced/capabilities
```

## 🔧 Development Setup

### 1. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install
```

### 2. Initialize Services

```bash
# Initialize NLP models
python -c "from services.nlp_service import initialize_nlp_models; import asyncio; asyncio.run(initialize_nlp_models())"

# Initialize enhanced services
python -c "from services.enhanced_nlp_service import initialize_enhanced_nlp; import asyncio; asyncio.run(initialize_enhanced_nlp())"
```

### 3. Train ML Models

```bash
# Train with example data
python data/example_data.py
```

## 🚀 Production Deployment

### Monolithic Deployment

```bash
# Build and deploy
docker-compose up -d --build

# Scale if needed
docker-compose up -d --scale backend=3
```

### Microservices Deployment

```bash
# Deploy microservices
docker-compose -f docker-compose.microservices.yml up -d --build

# Scale individual services
docker-compose -f docker-compose.microservices.yml up -d --scale ml-service=2
docker-compose -f docker-compose.microservices.yml up -d --scale ocr-service=2
```

## 🔍 Troubleshooting

### Common Issues

1. **ML Models not training:**
   - Check if `ENABLE_ML_MODELS=true`
   - Ensure sufficient training data
   - Check model directory permissions

2. **LLM not working:**
   - Verify API keys are set
   - Check `ENABLE_LLM=true`
   - Verify network connectivity

3. **OCR failing:**
   - Ensure Tesseract is installed
   - Check `ENABLE_OCR=true`
   - Verify image file formats

4. **Bias detection not working:**
   - Check `ENABLE_BIAS_DETECTION=true`
   - Verify sufficient candidate data
   - Check bias detection thresholds

### Logs and Debugging

```bash
# View service logs
docker-compose logs backend
docker-compose logs ml-service
docker-compose logs ocr-service

# Debug specific service
docker-compose exec backend python -c "from services.enhanced_nlp_service import get_enhanced_service_capabilities; import asyncio; print(asyncio.run(get_enhanced_service_capabilities()))"
```

## 📈 Performance Optimization

### Resource Requirements

**Minimum:**
- 4GB RAM
- 2 CPU cores
- 10GB storage

**Recommended:**
- 8GB RAM
- 4 CPU cores
- 50GB storage

**Production:**
- 16GB RAM
- 8 CPU cores
- 100GB storage

### Scaling Guidelines

1. **ML Models:** Scale based on training data size
2. **OCR:** Scale based on image processing volume
3. **LLM:** Scale based on API rate limits
4. **Ontology:** Scale based on knowledge graph size
5. **Bias Detection:** Scale based on candidate volume

## 🔒 Security Considerations

1. **API Keys:** Store securely, never commit to version control
2. **Bias Data:** Anonymize sensitive information
3. **File Uploads:** Validate file types and sizes
4. **Rate Limiting:** Implement proper rate limiting
5. **CORS:** Configure CORS properly for production

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [spaCy Documentation](https://spacy.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [MongoDB Best Practices](https://docs.mongodb.com/manual/core/best-practices/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

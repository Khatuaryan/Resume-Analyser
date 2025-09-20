# 🚀 START NOW - One Command Setup

## Quick Start (Choose Your Platform)

### For macOS/Linux Users:
```bash
# Run the automated setup script
./scripts/quick-start.sh
```

### For Windows Users:
```cmd
# Run the automated setup script
scripts\quick-start.bat
```

### Manual Setup (If scripts don't work):
```bash
# 1. Create environment file
cp env.example .env

# 2. Start services (Monolithic - Recommended)
docker-compose up -d

# 3. Wait for services to start (2-3 minutes)
# 4. Open http://localhost:3000 in your browser
```

## 🎯 What Happens Next

1. **Services Start**: Docker builds and starts all containers
2. **Database Initializes**: MongoDB sets up with example data
3. **Frontend Loads**: React app becomes available at http://localhost:3000
4. **Backend API Ready**: FastAPI serves at http://localhost:8000

## 👤 Login Credentials

### HR User (Post jobs, view candidates)
- **Email**: hr@techcorp.com
- **Password**: password123

### Candidate User (Upload resume, apply jobs)
- **Email**: candidate1@email.com
- **Password**: password123

## 🔧 If Something Goes Wrong

### Check if services are running:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs -f
```

### Restart everything:
```bash
docker-compose down
docker-compose up -d
```

### Reset completely:
```bash
docker-compose down -v
docker-compose up -d --build
```

## 📱 Access Points

- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎉 You're Ready!

Once you see the login page at http://localhost:3000, you're all set to use the Smart Resume Analyzer Platform!

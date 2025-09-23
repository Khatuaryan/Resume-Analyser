# 🚀 Quick Firebase Setup (5 Minutes)

## Step 1: Create Firebase Project (2 minutes)

1. **Go to**: https://console.firebase.google.com/
2. **Click**: "Create a project" or "Add project"
3. **Project name**: `resume-analyzer-platform`
4. **Enable Google Analytics**: Yes (recommended)
5. **Click**: "Create project"

## Step 2: Enable Firestore Database (1 minute)

1. **In your Firebase project**, go to **"Firestore Database"**
2. **Click**: "Create database"
3. **Choose**: "Start in test mode" (for development)
4. **Select location**: Choose closest to you (e.g., us-central1)
5. **Click**: "Done"

## Step 3: Get Service Account (2 minutes)

1. **Go to**: Project Settings (gear icon)
2. **Click**: "Service accounts" tab
3. **Click**: "Generate new private key"
4. **Download** the JSON file
5. **Rename** it to `firebase-service-account.json`
6. **Place** it in your project root (same level as docker-compose.yml)

## Step 4: Run Docker (Automatic!)

```bash
# This will automatically:
# 1. Initialize Firebase connection
# 2. Create admin user
# 3. Create sample data
# 4. Start the application
docker-compose up -d
```

## ✅ That's It!

Your application will be running at:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Firebase Console**: https://console.firebase.google.com/

## 🔍 View Your Data

1. **Go to**: https://console.firebase.google.com/
2. **Select** your project
3. **Click**: "Firestore Database"
4. **View** your collections: `users`, `resumes`, `jobs`

## 🎯 Login Credentials

- **Admin**: admin@resumeanalyzer.com / password123@
- **Candidate 1**: candidate1@email.com / password123
- **Candidate 2**: candidate2@email.com / password123

## 🆘 If Something Goes Wrong

```bash
# Check logs
docker-compose logs backend

# Restart if needed
docker-compose restart backend
```

That's it! Firebase is much easier than MongoDB! 🎉

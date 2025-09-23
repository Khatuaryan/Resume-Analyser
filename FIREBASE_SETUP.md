# 🔥 Firebase Setup Guide

## Step 1: Create Firebase Project

1. **Go to**: https://console.firebase.google.com/
2. **Click**: "Create a project" or "Add project"
3. **Project name**: `resume-analyzer-platform`
4. **Enable Google Analytics**: Yes (recommended)
5. **Click**: "Create project"

## Step 2: Enable Firestore Database

1. **In your Firebase project**, go to **"Firestore Database"**
2. **Click**: "Create database"
3. **Choose**: "Start in test mode" (for development)
4. **Select location**: Choose closest to you (e.g., us-central1)
5. **Click**: "Done"

## Step 3: Get Firebase Service Account

1. **Go to**: Project Settings (gear icon)
2. **Click**: "Service accounts" tab
3. **Click**: "Generate new private key"
4. **Download** the JSON file
5. **Rename** it to `firebase-service-account.json`
6. **Place** it in your project root directory

## Step 4: Install Firebase Dependencies

```bash
# Install Firebase dependencies
pip install firebase-admin google-cloud-firestore python-dotenv

# Or install from requirements file
pip install -r backend/requirements_firebase.txt
```

## Step 5: Set Environment Variables

Create a `.env` file in your project root:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=resume-analyzer-platform
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
DATABASE_TYPE=firebase
DATABASE_NAME=resume_analyzer

# Other settings
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Step 6: Initialize Firebase Data

```bash
# Run the setup script
python backend/scripts/setup_firebase.py
```

## Step 7: View Your Data

1. **Go to**: https://console.firebase.google.com/
2. **Select** your project
3. **Click**: "Firestore Database"
4. **View** your collections: `users`, `resumes`, `jobs`, etc.

## 🎯 Benefits of Firebase

- ✅ **Easy to use** web interface
- ✅ **Real-time** data updates
- ✅ **No complex** authentication setup
- ✅ **Automatic** scaling
- ✅ **Built-in** security rules
- ✅ **Easy** data visualization

## 📊 Your Data Structure

### Collections:
- **`users`** - User accounts (admin, candidates, HR)
- **`resumes`** - Uploaded resumes and processing status
- **`jobs`** - Job postings
- **`applications`** - Job applications
- **`candidate_rankings`** - Candidate rankings
- **`resume_analysis`** - Resume analysis data
- **`skill_recommendations`** - Skill recommendations

### Sample Data:
- **3 users** (1 admin + 2 candidates)
- **2 resumes** with parsed data
- **Skills extracted**: Python, JavaScript, React, Node.js, Java, Spring Boot, MySQL, AWS
- **Experience data**: Software Developer, Backend Developer
- **Education data**: Bachelor of Computer Science, Master of Software Engineering

## 🔧 Firebase Console Features

- **Data Viewer**: See all your data in a nice table format
- **Query Builder**: Build complex queries visually
- **Real-time Updates**: See changes as they happen
- **Export/Import**: Easy data management
- **Security Rules**: Configure access permissions
- **Analytics**: Track usage and performance

## 🚀 Next Steps

1. **Complete** the Firebase setup above
2. **Run** the setup script to populate data
3. **View** your data in the Firebase console
4. **Update** your backend to use Firebase instead of MongoDB
5. **Test** the integration

Firebase is much easier to use than MongoDB and provides a great web interface for viewing and managing your data! 🎉

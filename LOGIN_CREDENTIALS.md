# 🔐 Login Credentials

## Quick Start Login

After running `docker-compose up -d`, you can immediately login with these credentials:

### 👨‍💼 Admin (HR) Login
- **Email**: `admin@resumeanalyzer.com`
- **Password**: `password123@`
- **Role**: HR Administrator
- **Access**: Full system access, job management, candidate analysis

### 👤 Candidate Access
- **Registration**: Candidates can register new accounts
- **No Sample Users**: System is ready for real candidate registrations
- **Role**: Candidate

## 🚀 Quick Test

Run this command to test all login credentials:
```bash
./test-login.sh
```

## 🔧 Automatic Setup

The system automatically creates these users when you start the application:

1. **Firebase Setup**: Runs automatically on backend startup
2. **User Creation**: Creates admin and candidate users if they don't exist
3. **Data Population**: Adds sample resumes and job data
4. **No Manual Setup Required**: Everything works out of the box

## 📱 Access Points

- **Main Application**: http://localhost
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## 🛠️ Troubleshooting

If login fails:

1. **Check Backend Status**:
   ```bash
   docker-compose logs backend
   ```

2. **Verify Firebase Setup**:
   Look for "✅ Firebase setup completed" in the logs

3. **Test API Directly**:
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@resumeanalyzer.com", "password": "password123@"}'
   ```

4. **Restart Services**:
   ```bash
   docker-compose restart backend
   ```

## 🔄 Data Persistence

- **Firebase Firestore**: All data is stored in Firebase
- **Persistent**: Data survives `docker-compose down` and `docker-compose up -d`
- **Automatic**: No need to recreate users after restart
- **Cloud-Based**: Access your data from anywhere

## 📊 System Data

The system comes with:
- ✅ 1 Admin user (HR)
- ✅ 0 Candidate users (ready for real registrations)
- ✅ 0 Sample resumes (ready for real uploads)
- ✅ Ready-to-use job matching system

## 🎯 Next Steps

1. **Login as Admin**: Create job postings
2. **Register Candidates**: Create new candidate accounts
3. **Upload Resumes**: Candidates can upload and analyze resumes
4. **Explore Features**: Skills analysis, job matching, analytics

---

**🎉 You're all set! The system is ready to use immediately after `docker-compose up -d`**

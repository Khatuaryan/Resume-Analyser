#!/bin/bash

echo "🧪 Testing Resume Analyzer Login Credentials"
echo "=============================================="

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 5

# Test admin login
echo "🔐 Testing Admin Login..."
ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@resumeanalyzer.com", "password": "password123@"}')

if echo "$ADMIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Admin login successful!"
    echo "   Email: admin@resumeanalyzer.com"
    echo "   Password: password123@"
else
    echo "❌ Admin login failed"
    echo "Response: $ADMIN_RESPONSE"
fi

echo ""

# Test candidate login (no sample candidates available)
echo "🔐 Testing Candidate Login..."
echo "⚠️  No sample candidates available - system ready for real users"

echo ""
echo "🎯 Login Test Complete!"
echo ""
echo "📋 Available Login Credentials:"
echo "   Admin (HR): admin@resumeanalyzer.com / password123@"
echo "   Candidates: Register new accounts to get started"
echo ""
echo "🌐 Access the application at: http://localhost"

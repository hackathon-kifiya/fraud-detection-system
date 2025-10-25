#!/bin/bash

echo "=== Testing Fraud Detection System Integration ==="
echo

# Test backend health
echo "1. Testing backend health..."
HEALTH_RESPONSE=$(curl -s http://localhost:4000/health)
if [ $? -eq 0 ]; then
    echo "✅ Backend is running"
    echo "Response: $HEALTH_RESPONSE"
else
    echo "❌ Backend is not responding"
fi
echo

# Test login
echo "2. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:4000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@fraud-detection.com","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | grep -q "token"; then
    echo "✅ Login successful"
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
    echo "Token received: ${TOKEN:0:50}..."
else
    echo "❌ Login failed"
    echo "Response: $LOGIN_RESPONSE"
fi
echo

# Test protected endpoint
echo "3. Testing protected endpoint..."
if [ ! -z "$TOKEN" ]; then
    USERS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4000/api/users)
    if echo "$USERS_RESPONSE" | grep -q "users"; then
        echo "✅ Protected endpoint working"
        USER_COUNT=$(echo "$USERS_RESPONSE" | jq '.users | length')
        echo "Found $USER_COUNT users"
    else
        echo "❌ Protected endpoint failed"
        echo "Response: $USERS_RESPONSE"
    fi
else
    echo "⚠️  Skipping protected endpoint test (no token)"
fi
echo

# Test frontend
echo "4. Testing frontend..."
FRONTEND_RESPONSE=$(curl -s -I http://localhost:3000 | head -1)
if echo "$FRONTEND_RESPONSE" | grep -q "200"; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend is not responding"
fi
echo

echo "=== Integration Test Complete ==="
echo
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:4000"
echo "📊 Health Check: http://localhost:4000/health"
echo
echo "Demo credentials:"
echo "  admin@fraud-detection.com / admin123"
echo "  analyst@fraud-detection.com / analyst123"
echo "  viewer@fraud-detection.com / viewer123"

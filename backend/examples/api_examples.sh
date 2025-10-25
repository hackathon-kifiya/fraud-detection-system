#!/bin/bash

# API Examples for User Management Module
# Make sure the server is running on localhost:4000

BASE_URL="http://localhost:4000"

echo "=== User Management API Examples ==="
echo

# 1. Register a new user
echo "1. Registering a new user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "analyst"
  }')

echo "Register Response: $REGISTER_RESPONSE"
echo

# 2. Login
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }')

echo "Login Response: $LOGIN_RESPONSE"
echo

# Extract token from login response (requires jq)
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token')
echo "Extracted Token: $TOKEN"
echo

# 3. Get current user info
echo "3. Getting user info..."
USER_INFO=$(curl -s -X GET "$BASE_URL/api/users" \
  -H "Authorization: Bearer $TOKEN")

echo "User List Response: $USER_INFO"
echo

# 4. Update user
echo "4. Updating user..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/users/$(echo $USER_INFO | jq -r '.users[0].id')" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name"
  }')

echo "Update Response: $UPDATE_RESPONSE"
echo

# 5. Change password
echo "5. Changing password..."
CHANGE_PASSWORD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/users/$(echo $USER_INFO | jq -r '.users[0].id')/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "testpassword123",
    "new_password": "newpassword123"
  }')

echo "Change Password Response: $CHANGE_PASSWORD_RESPONSE"
echo

echo "=== API Examples Complete ==="

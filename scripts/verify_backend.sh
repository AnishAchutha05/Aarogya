#!/bin/bash
set -e

echo "======================================"
echo "Aarogya Backend End-to-End Verification"
echo "======================================"

# Variables
API_URL="http://localhost:8000"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="securepassword123"

# 1. Health check
echo "[1] Checking Health Endpoint..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health || echo "000")
if [ "$HEALTH_STATUS" -ne 200 ]; then
  echo "❌ Health check failed. API is not running or returning 200."
  exit 1
fi
echo "✅ Health check passed."

# 2. Register
echo "[2] Testing Registration..."
REGISTER_RES=$(curl -s -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\", \"password\":\"$TEST_PASSWORD\", \"name\":\"Test User\"}")

# Allow 409 Conflict if already registered
if echo "$REGISTER_RES" | grep -q "email" || echo "$REGISTER_RES" | grep -q "already registered"; then
  echo "✅ Registration endpoint responded properly."
else
  echo "❌ Registration failed. Response: $REGISTER_RES"
  exit 1
fi

# 3. Login
echo "[3] Testing Login..."
LOGIN_RES=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\", \"password\":\"$TEST_PASSWORD\"}")

ACCESS_TOKEN=$(echo $LOGIN_RES | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed. Response: $LOGIN_RES"
  exit 1
fi
echo "✅ Login passed."

# 4. Access Protected Route (Profile)
echo "[4] Testing Protected Route (Profile)..."
PROFILE_RES=$(curl -s -X GET $API_URL/users/me \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$PROFILE_RES" | grep -q "$TEST_EMAIL"; then
  echo "✅ Protected route passed."
else
  echo "❌ Protected route failed. Response: $PROFILE_RES"
  exit 1
fi

echo ""
echo "======================================"
echo "🎉 Basic API Verification Successful!"
echo "======================================"

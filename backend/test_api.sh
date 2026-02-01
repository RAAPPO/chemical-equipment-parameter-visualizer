#!/bin/bash

echo "🧪 Testing API Endpoints"
echo "========================"
echo ""

# Get token
echo "1. Getting JWT token..."
TOKEN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8100/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')

# Extract access token
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token"
  echo $TOKEN_RESPONSE
  exit 1
fi

echo "✅ Token obtained"
echo ""

# Test endpoints
echo "2. Testing health check..."
curl -s http://127.0.0.1:8100/api/health/
echo -e "\n"

echo "3. Getting datasets..."
curl -s http://127.0.0.1:8100/api/datasets/ -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "4. Uploading sample CSV..."
UPLOAD=$(curl -s -X POST http://127.0.0.1:8100/api/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@../sample-data/sample_equipment_data.csv")

echo $UPLOAD
echo ""

# Extract dataset ID
DATASET_ID=$(echo $UPLOAD | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ ! -z "$DATASET_ID" ]; then
  echo "5. Getting analytics for dataset: $DATASET_ID"
  curl -s http://127.0.0.1:8100/api/datasets/$DATASET_ID/analytics/ \
    -H "Authorization: Bearer $TOKEN"
  echo ""
fi

echo ""
echo "✅ Testing complete!"

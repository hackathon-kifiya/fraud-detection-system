#!/bin/bash

# Test script for Case Assignment API
# This script tests the case assignment endpoints

BASE_URL="http://localhost:4000"

echo "Testing Case Assignment API Endpoints"
echo "====================================="

# Test 1: Get unassigned cases (admin endpoint)
echo "1. Testing GET /api/admin/cases/unassigned"
curl -X GET "$BASE_URL/api/admin/cases/unassigned?limit=5&offset=0" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  | jq '.' 2>/dev/null || echo "Response received"

echo -e "\n"

# Test 2: Get case assignments (admin endpoint)
echo "2. Testing GET /api/admin/cases/assignments"
curl -X GET "$BASE_URL/api/admin/cases/assignments?limit=5&offset=0" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  | jq '.' 2>/dev/null || echo "Response received"

echo -e "\n"

# Test 3: Get auditor workload (admin endpoint)
echo "3. Testing GET /api/admin/auditors/workload"
curl -X GET "$BASE_URL/api/admin/auditors/workload" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  | jq '.' 2>/dev/null || echo "Response received"

echo -e "\n"

# Test 4: Get my assignments (auditor endpoint)
echo "4. Testing GET /api/audit/my-assignments"
curl -X GET "$BASE_URL/api/audit/my-assignments?limit=5&offset=0" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer auditor-token" \
  | jq '.' 2>/dev/null || echo "Response received"

echo -e "\n"

# Test 5: Test assignment creation (admin endpoint)
echo "5. Testing POST /api/admin/cases/assign"
curl -X POST "$BASE_URL/api/admin/cases/assign" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{
    "flagged_item_id": "test-flagged-item-id",
    "auditor_id": "test-auditor-id",
    "priority": "high",
    "notes": "Test assignment"
  }' \
  | jq '.' 2>/dev/null || echo "Response received"

echo -e "\n"

# Test 6: Test bulk assignment (admin endpoint)
echo "6. Testing POST /api/admin/cases/bulk-assign"
curl -X POST "$BASE_URL/api/admin/cases/bulk-assign" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{
    "flagged_item_ids": ["test-flagged-item-1", "test-flagged-item-2"],
    "auditor_id": "test-auditor-id",
    "priority": "medium",
    "notes": "Bulk test assignment"
  }' \
  | jq '.' 2>/dev/null || echo "Response received"

echo -e "\n"

echo "API Testing Complete!"
echo "Note: Some endpoints may return errors due to missing data or authentication, but the important thing is that the endpoints are accessible and the server responds."

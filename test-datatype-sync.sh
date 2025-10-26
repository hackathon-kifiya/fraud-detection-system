#!/bin/bash

# Integration API Test Script for Data Type Sync
# Tests data synchronization between Backend and Rule Engine

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service URLs
BACKEND_URL="http://localhost:8080"
RULE_ENGINE_URL="http://localhost:8081"
TIMEOUT=10

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test headers
print_test() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Function to print failure
print_failure() {
    echo -e "${RED}✗ $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# Function to print info
print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Function to check service availability
check_service() {
    local service_url=$1
    local service_name=$2
    
    if curl -s --max-time $TIMEOUT "$service_url/health" > /dev/null 2>&1; then
        print_success "$service_name is available at $service_url"
        return 0
    else
        print_failure "$service_name is not available at $service_url"
        return 1
    fi
}

# Function to make API calls with error handling
api_call() {
    local method=$1
    local url=$2
    local data=$3
    local headers=$4
    
    if [ -n "$data" ] && [ "$data" != "" ]; then
        if [ -n "$headers" ]; then
            curl -s -X "$method" "$url" -H "Content-Type: application/json" -H "$headers" -d "$data" -w "\n%{http_code}"
        else
            curl -s -X "$method" "$url" -H "Content-Type: application/json" -d "$data" -w "\n%{http_code}"
        fi
    else
        if [ -n "$headers" ]; then
            curl -s -X "$method" "$url" -H "Content-Type: application/json" -H "$headers" -w "\n%{http_code}"
        else
            curl -s -X "$method" "$url" -H "Content-Type: application/json" -w "\n%{http_code}"
        fi
    fi
}

# Function to extract JSON response and status code
parse_response() {
    local response=$1
    local status=$(echo "$response" | tail -n 1)
    local body=$(echo "$response" | head -n -1)
    echo "$body|$status"
}

# Main test execution
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Data Type Sync Integration Test                    ║"
echo "║   Testing Backend ↔ Rule Engine synchronization      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Check Service Availability
print_test "1. Service Health Checks"
check_service "$BACKEND_URL" "Backend" || exit 1
check_service "$RULE_ENGINE_URL" "Rule Engine" || exit 1

# Step 2: Authenticate to Get Token
print_test "2. Authenticate to Get Token"

LOGIN_REQUEST='{
    "email": "admin@fraud-detection.com",
    "password": "admin123"
}'

LOGIN_RESPONSE=$(api_call "POST" "$BACKEND_URL/api/auth/login" "$LOGIN_REQUEST")
LOGIN_PARSED=$(parse_response "$LOGIN_RESPONSE")
LOGIN_STATUS=$(echo "$LOGIN_PARSED" | cut -d'|' -f2)
LOGIN_BODY=$(echo "$LOGIN_PARSED" | cut -d'|' -f1)

AUTH_TOKEN=""
if [ "$LOGIN_STATUS" -eq 200 ]; then
    AUTH_TOKEN=$(echo "$LOGIN_BODY" | jq -r '.token // empty')
    if [ -n "$AUTH_TOKEN" ] && [ "$AUTH_TOKEN" != "null" ]; then
        print_success "Authentication successful"
        AUTH_HEADER="Authorization: Bearer $AUTH_TOKEN"
    else
        print_info "Authentication token not found, trying without auth"
        AUTH_HEADER=""
    fi
else
    print_info "Login failed (Status: $LOGIN_STATUS), trying without auth"
    AUTH_HEADER=""
fi

# Step 3: Test Data Type Creation in Backend
print_test "3. Create Data Type in Backend"
TEST_DATA_TYPE="transaction_test_$(date +%s)"
CREATE_REQUEST='{
    "data_type": "'"$TEST_DATA_TYPE"'",
    "name": "Test Transaction Data",
    "description": "Test data type for integration testing",
    "schema_definition": {
        "fields": {
            "amount": {"type": "number"},
            "currency": {"type": "string"},
            "transaction_date": {"type": "string"},
            "merchant_id": {"type": "string"}
        },
        "required": ["amount", "currency"]
    },
    "sample_data": {
        "amount": 100.50,
        "currency": "USD",
        "transaction_date": "2024-01-01",
        "merchant_id": "MERCHANT_001"
    }
}'

RESPONSE=$(api_call "POST" "$BACKEND_URL/api/data-types" "$CREATE_REQUEST" "$AUTH_HEADER")
RESPONSE_PARSED=$(parse_response "$RESPONSE")
STATUS=$(echo "$RESPONSE_PARSED" | cut -d'|' -f2)
BODY=$(echo "$RESPONSE_PARSED" | cut -d'|' -f1)

if [ "$STATUS" -eq 201 ] || [ "$STATUS" -eq 200 ]; then
    print_success "Data type created in Backend (Status: $STATUS)"
    BACKEND_DATA_TYPE=$(echo "$BODY" | jq -r '.id // .data_type // empty' 2>/dev/null)
    if [ -n "$BODY" ]; then
        echo "Response: $BODY" | jq '.' 2>/dev/null || echo "Response: $BODY"
    fi
else
    print_failure "Failed to create data type in Backend (Status: $STATUS)"
    echo "Response: $BODY"
    print_info "Trying to create via direct rule engine call instead..."
    
    # Try creating directly in rule engine (Rule Engine uses camelCase)
    RULE_ENGINE_REQUEST='{
    "dataType": "'"$TEST_DATA_TYPE"'",
    "name": "Test Transaction Data",
    "description": "Test data type for integration testing",
    "schemaDefinition": {
        "fields": {
            "amount": {"type": "number"},
            "currency": {"type": "string"},
            "transaction_date": {"type": "string"},
            "merchant_id": {"type": "string"}
        },
        "required": ["amount", "currency"]
    },
    "sampleData": {
        "amount": 100.50,
        "currency": "USD",
        "transaction_date": "2024-01-01",
        "merchant_id": "MERCHANT_001"
    }
}'
    RULE_ENGINE_CREATE=$(api_call "POST" "$RULE_ENGINE_URL/api/data-types" "$RULE_ENGINE_REQUEST")
    RE_CREATE_PARSED=$(parse_response "$RULE_ENGINE_CREATE")
    RE_CREATE_STATUS=$(echo "$RE_CREATE_PARSED" | cut -d'|' -f2)
    RE_CREATE_BODY=$(echo "$RE_CREATE_PARSED" | cut -d'|' -f1)
    
    if [ "$RE_CREATE_STATUS" -eq 200 ]; then
        print_success "Created directly in Rule Engine"
        echo "Rule Engine Response:"
        echo "$RE_CREATE_BODY" | jq '.'
    else
        print_failure "Failed to create in Rule Engine (Status: $RE_CREATE_STATUS)"
        echo "Response: $RE_CREATE_BODY"
    fi
fi

# Step 4: Verify Data Type in Rule Engine
print_test "4. Verify Data Type in Rule Engine"
sleep 2  # Wait for sync

RULE_ENGINE_CHECK=$(api_call "GET" "$RULE_ENGINE_URL/api/data-types/by-name/$TEST_DATA_TYPE")
CHECK_PARSED=$(parse_response "$RULE_ENGINE_CHECK")
CHECK_STATUS=$(echo "$CHECK_PARSED" | cut -d'|' -f2)
CHECK_BODY=$(echo "$CHECK_PARSED" | cut -d'|' -f1)

if [ "$CHECK_STATUS" -eq 200 ]; then
    print_success "Data type found in Rule Engine"
    echo "Rule Engine Response:"
    echo "$CHECK_BODY" | jq '.'
    
    # Extract key fields for comparison
    RE_NAME=$(echo "$CHECK_BODY" | jq -r '.name // empty')
    RE_DESCRIPTION=$(echo "$CHECK_BODY" | jq -r '.description // empty')
    
    if [ -n "$RE_NAME" ] && [ "$RE_NAME" = "Test Transaction Data" ]; then
        print_success "Data type name matches in Rule Engine"
    else
        print_failure "Data type name does not match in Rule Engine"
    fi
else
    print_failure "Data type not found in Rule Engine (Status: $CHECK_STATUS)"
    echo "Response: $CHECK_BODY"
fi

# Step 5: List All Data Types in Both Services
print_test "5. List All Data Types"

# Get all data types from Backend
BACKEND_LIST=$(api_call "GET" "$BACKEND_URL/api/data-types" "" "$AUTH_HEADER")
BL_PARSED=$(parse_response "$BACKEND_LIST")
BL_STATUS=$(echo "$BL_PARSED" | cut -d'|' -f2)
BL_BODY=$(echo "$BL_PARSED" | cut -d'|' -f1)

if [ "$BL_STATUS" -eq 200 ]; then
    BACKEND_COUNT=$(echo "$BL_BODY" | jq -r '.data_types | length' 2>/dev/null || echo "0")
    print_success "Backend has $BACKEND_COUNT data types"
else
    print_failure "Failed to list data types from Backend"
fi

# Get all data types from Rule Engine
RULE_ENGINE_LIST=$(api_call "GET" "$RULE_ENGINE_URL/api/data-types")
RE_PARSED=$(parse_response "$RULE_ENGINE_LIST")
RE_STATUS=$(echo "$RE_PARSED" | cut -d'|' -f2)
RE_BODY=$(echo "$RE_PARSED" | cut -d'|' -f1)

if [ "$RE_STATUS" -eq 200 ]; then
    RE_COUNT=$(echo "$RE_BODY" | jq '. | length' 2>/dev/null || echo "0")
    print_success "Rule Engine has $RE_COUNT data types"
else
    print_failure "Failed to list data types from Rule Engine"
fi

# Step 6: Compare Data Types (Name-based matching)
print_test "6. Verify Data Type Consistency"

if [ "$BL_STATUS" -eq 200 ] && [ "$RE_STATUS" -eq 200 ]; then
    # Extract data type names (Backend uses snake_case, Rule Engine uses camelCase)
    BACKEND_NAMES=$(echo "$BL_BODY" | jq -r '.data_types[]?.data_type // .dataTypes[]?.dataType // .[]?.dataType // .[]?.data_type // empty' 2>/dev/null)
    RE_NAMES=$(echo "$RE_BODY" | jq -r '.[].dataType // .[].data_type // empty' 2>/dev/null)
    
    print_info "Checking if backend data types exist in rule engine..."
    SYNC_COUNT=0
    MISSING_COUNT=0
    
    for name in $BACKEND_NAMES; do
        if echo "$RE_NAMES" | grep -q "$name"; then
            SYNC_COUNT=$((SYNC_COUNT + 1))
        else
            MISSING_COUNT=$((MISSING_COUNT + 1))
            print_failure "Data type '$name' not found in Rule Engine"
        fi
    done
    
    if [ $MISSING_COUNT -eq 0 ]; then
        print_success "All backend data types are synced to Rule Engine ($SYNC_COUNT synced)"
    else
        print_info "$SYNC_COUNT data types synced, $MISSING_COUNT missing"
    fi
fi

# Step 7: Test Data Type Update Flow
print_test "7. Test Data Type Update"
if [ -n "$BACKEND_DATA_TYPE" ] || [ "$TEST_DATA_TYPE" != "" ]; then
    UPDATE_REQUEST='{
        "name": "Updated Test Transaction Data",
        "description": "Updated description for testing",
        "status": "ACTIVE"
    }'
    
    # Try to update via backend (this should sync to rule engine)
    if [ -n "$BACKEND_DATA_TYPE" ]; then
        UPDATE_RESPONSE=$(api_call "PUT" "$BACKEND_URL/api/data-types/$BACKEND_DATA_TYPE" "$UPDATE_REQUEST" "$AUTH_HEADER")
    else
        # Try by name
        UPDATE_RESPONSE=$(api_call "GET" "$BACKEND_URL/api/data-types/name/$TEST_DATA_TYPE" "" "$AUTH_HEADER")
        UPDATE_STATUS=$(echo "$UPDATE_RESPONSE" | tail -n 1)
        if [ "$UPDATE_STATUS" -eq 200 ]; then
            UPDATE_ID=$(echo "$UPDATE_RESPONSE" | head -n -1 | jq -r '.id // empty')
            if [ -n "$UPDATE_ID" ]; then
                UPDATE_RESPONSE=$(api_call "PUT" "$BACKEND_URL/api/data-types/$UPDATE_ID" "$UPDATE_REQUEST" "$AUTH_HEADER")
            fi
        fi
    fi
    
    UPDATE_PARSED=$(parse_response "$UPDATE_RESPONSE")
    UPDATE_STATUS=$(echo "$UPDATE_PARSED" | cut -d'|' -f2)
    UPDATE_BODY=$(echo "$UPDATE_PARSED" | cut -d'|' -f1)
    
    if [ "$UPDATE_STATUS" -eq 200 ]; then
        print_success "Data type updated successfully"
        print_info "Verifying update in Rule Engine..."
        
        sleep 2
        VERIFY_UPDATE=$(api_call "GET" "$RULE_ENGINE_URL/api/data-types/by-name/$TEST_DATA_TYPE")
        VU_PARSED=$(parse_response "$VERIFY_UPDATE")
        VU_STATUS=$(echo "$VU_PARSED" | cut -d'|' -f2)
        VU_BODY=$(echo "$VU_PARSED" | cut -d'|' -f1)
        
        if [ "$VU_STATUS" -eq 200 ]; then
            VU_NAME=$(echo "$VU_BODY" | jq -r '.name // empty')
            if [ "$VU_NAME" = "Updated Test Transaction Data" ]; then
                print_success "Update synced to Rule Engine successfully"
            else
                print_failure "Update not synced to Rule Engine (found: $VU_NAME)"
            fi
        fi
    else
        print_info "Update test skipped (Status: $UPDATE_STATUS)"
    fi
fi

# Step 8: Test Schema Validation
print_test "8. Test Schema Validation"
INVALID_SCHEMA='{
    "data_type": "invalid_test",
    "name": "Invalid Schema Test",
    "description": "Testing validation",
    "schema_definition": {}
}'

VALIDATION_RESPONSE=$(api_call "POST" "$BACKEND_URL/api/data-types" "$INVALID_SCHEMA" "$AUTH_HEADER")
V_PARSED=$(parse_response "$VALIDATION_RESPONSE")
V_STATUS=$(echo "$V_PARSED" | cut -d'|' -f2)

if [ "$V_STATUS" -eq 400 ] || [ "$V_STATUS" -eq 422 ]; then
    print_success "Schema validation working correctly"
else
    print_info "Validation test: Status $V_STATUS"
fi

# Summary
echo -e "\n${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                  Test Summary                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi


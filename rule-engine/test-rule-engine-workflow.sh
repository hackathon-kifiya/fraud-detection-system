#!/bin/bash

# Rule Engine Service - Comprehensive Workflow Test Script
# This script performs blackbox testing of all Rule Engine APIs

set +e  # Don't exit on error - continue to show all failures

BASE_URL="http://localhost:8081"
DATA_MANAGEMENT_URL="http://localhost:5004"
TEST_PASSED=0
TEST_FAILED=0
FAILED_TESTS=()

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for jq dependency
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed.${NC}"
    echo "Install with: sudo pacman -S jq (Arch) or sudo apt install jq (Debian/Ubuntu)"
    exit 1
fi

# Utility functions
log_test() {
    local test_name=$1
    local status=$2
    local message=$3
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name${NC}"
        ((TEST_PASSED++))
    elif [ "$status" = "SKIP" ]; then
        echo -e "${YELLOW}⊘${NC} $test_name - $message${NC}"
        # Don't increment counters for skipped tests
    else
        echo -e "${RED}✗${NC} $test_name - $message${NC}"
        ((TEST_FAILED++))
        FAILED_TESTS+=("$test_name")
    fi
}

log_info() {
    echo -e "${YELLOW}→${NC} $1${NC}"
}

extract_id() {
    local json="$1"
    # Try jq first, fallback to grep/sed
    local id=$(echo "$json" | jq -r '.id' 2>/dev/null)
    if [ -z "$id" ] || [ "$id" = "null" ]; then
        id=$(echo "$json" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    fi
    echo "$id"
}

extract_id_from_list() {
    local list="$1"
    local index="${2:-0}"
    echo "$list" | jq -r ".[$index].id" 2>/dev/null || echo ""
}

extract_field() {
    local json="$1"
    local field="$2"
    local value=$(echo "$json" | jq -r ".$field" 2>/dev/null)
    if [ -z "$value" ] || [ "$value" = "null" ]; then
        value=$(echo "$json" | grep -o "\"$field\":\"[^\"]*\"" | head -1 | cut -d'"' -f4)
    fi
    echo "$value"
}

# Extract boolean field (handles true/false without quotes)
extract_boolean_field() {
    local json="$1"
    local field="$2"
    
    # Try jq first
    local value=$(echo "$json" | jq -r ".$field" 2>/dev/null)
    
    # If empty or null, try grep/sed
    if [ -z "$value" ] || [ "$value" = "null" ]; then
        value=$(echo "$json" | grep -o "\"$field\":\s*\(true\|false\)" | grep -o 'true\|false')
    fi
    
    echo "$value"
}

# Extract numeric or string field (handles numbers, strings, etc.)
extract_value() {
    local json="$1"
    local field="$2"
    
    # Try jq first
    local value=$(echo "$json" | jq -r ".$field" 2>/dev/null)
    
    # If empty or null, try grep/sed for numeric or unquoted values
    if [ -z "$value" ] || [ "$value" = "null" ]; then
        value=$(echo "$json" | grep -o "\"$field\":[^,}]*" | grep -o ':[^,}]*' | sed 's/://' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    fi
    
    # Try string values in quotes
    if [ -z "$value" ] || [ "$value" = "null" ]; then
        value=$(echo "$json" | grep -o "\"$field\":\s*\"[^\"]*\"" | head -1 | grep -o '"[^"]*"' | tr -d '"')
    fi
    
    echo "$value"
}

# Test helpers
check_http_status() {
    local response="$1"
    local expected="$2"
    local actual=$(echo "$response" | tail -1)
    [ "$actual" = "$expected" ]
}

make_request() {
    local method=$1
    local url=$2
    local data="$3"
    local headers="$4"
    
    if [ -n "$data" ]; then
        curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -H "$headers" \
            -d "$data"
    else
        curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "$headers"
    fi
}

# ============================================================================
# Database Cleanup
# ============================================================================
clear_database() {
    echo ""
    echo "========================================="
    echo "Clearing Rule Engine Database"
    echo "========================================="
    
    log_info "Clearing rule tables..."
    
    # Clear the database using docker exec
    docker exec fraud-detection-system-postgres-1 psql -U frauduser -d frauddb -c "
        TRUNCATE TABLE rule CASCADE;
    " > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        log_info "Database cleared successfully"
    else
        echo -e "${RED}Warning: Failed to clear database.${NC}"
    fi
}

# ============================================================================
# CATEGORY 1: Health Check Tests
# ============================================================================
run_health_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 1: Health Check Tests"
    echo "========================================="
    
    local response=$(make_request "GET" "$BASE_URL/api/health" "" "")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Health Check" "PASS"
    else
        log_test "Health Check" "FAIL" "Status: $status"
    fi
}

# ============================================================================
# CATEGORY 2: Data Type Management Tests
# ============================================================================
run_data_type_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 2: Data Type Management Tests (via data-management-service)"
    echo "========================================="
    
    # Create data type via data-management-service
    log_info "Creating data type 'transaction' via data-management-service..."
    local create_request='{
        "data_type": "transaction",
        "name": "Transaction Data",
        "description": "Financial transaction data",
        "schema_definition": {
            "fields": {
                "amount": "Double",
                "accountBalance": "Double",
                "type": "String",
                "paymentMethod": "String"
            },
            "required": ["amount", "accountBalance"]
        },
        "sample_data": {
            "amount": 1000.0,
            "accountBalance": 5000.0,
            "type": "debit",
            "paymentMethod": "card"
        },
        "status": "ACTIVE",
        "created_by": "test-user"
    }'
    
    local response=$(make_request "POST" "$DATA_MANAGEMENT_URL/data-types" "$create_request" "")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "201" || check_http_status "$response" "200"; then
        log_test "Create Data Type via Data Management Service" "PASS"
    elif check_http_status "$response" "400" && echo "$body" | grep -q "already exists"; then
        log_test "Create Data Type via Data Management Service" "PASS" "(already exists)"
    else
        log_test "Create Data Type via Data Management Service" "FAIL" "Status: $status, Body: $body"
    fi
    
    # Get all data types
    log_info "Getting all data types from data-management-service..."
    response=$(make_request "GET" "$DATA_MANAGEMENT_URL/data-types" "" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Get All Data Types from Data Management Service" "PASS"
    else
        log_test "Get All Data Types from Data Management Service" "FAIL" "Status: $status"
    fi
    
    # Get data type by identifier
    log_info "Getting data type 'transaction' from data-management-service..."
    response=$(make_request "GET" "$DATA_MANAGEMENT_URL/data-types/transaction" "" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Get Data Type by Identifier" "PASS"
    else
        log_test "Get Data Type by Identifier" "FAIL" "Status: $status"
    fi
}

# ============================================================================
# CATEGORY 3: Rule Management Tests
# ============================================================================
run_rule_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 3: Rule Management Tests"
    echo "========================================="
    
    # Validate DRL syntax and semantics before creating rule
    log_info "Validating DRL syntax and semantics..."
    local validate_request='{
        "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"High Amount Alert\"\nwhen\n    $fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() > getPropertyAsNumber(\"accountBalance\").doubleValue() )\nthen\n    System.out.println(\"ALERT: Transaction amount exceeds account balance!\");\n    $fact.addViolation(\"HIGH_AMOUNT\", \"Transaction amount exceeds account balance\");\nend\n",
        "dataType": "transaction"
    }'
    
    local response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$validate_request" "")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -1)
    
    # Check if validation passed
    local is_valid=$(extract_boolean_field "$body" "valid")
    
    if [ -z "$is_valid" ] || [ "$is_valid" = "null" ]; then
        log_test "Validate DRL Syntax and Semantics" "FAIL" "Could not parse response: $body"
    elif check_http_status "$response" "200" && [ "$is_valid" = "true" ]; then
        log_test "Validate DRL Syntax and Semantics" "PASS"
    else
        log_test "Validate DRL Syntax and Semantics" "FAIL" "Status: $status, Valid: $is_valid"
    fi
    
    # Validate invalid DRL syntax (negative test) - Missing package declaration
    log_info "Validating invalid DRL - missing package declaration..."
    local invalid_validate_request='{
        "drlContent": "import com.frauddetection.domain.DynamicFact;\n\nrule \"Invalid Rule\"\nwhen\n    fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() > 100 )\nthen\n    fact.addViolation(\"ERROR\", \"This should fail validation\");\nend\n",
        "dataType": "transaction"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$invalid_validate_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    # Check if validation correctly identified invalid DRL
    is_valid=$(extract_boolean_field "$body" "valid")
    
    if check_http_status "$response" "200" && [ "$is_valid" = "false" ]; then
        log_test "Reject Invalid DRL - Missing Package" "PASS"
    else
        log_test "Reject Invalid DRL - Missing Package" "FAIL" "Status: $status, Valid: $is_valid (expected false)"
    fi
    
    # Validate invalid DRL syntax (negative test) - Syntax error in condition
    log_info "Validating invalid DRL - syntax error in condition..."
    invalid_validate_request='{
        "drlContent": "package rules;\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Invalid Condition\"\nwhen\n    fact : DynamicFact( getPropertyAsNumber(\"amount\") >\nthen\n    fact.addViolation(\"ERROR\", \"Unclosed condition\");\nend\n",
        "dataType": "transaction"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$invalid_validate_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    is_valid=$(extract_boolean_field "$body" "valid")
    
    if check_http_status "$response" "200" && [ "$is_valid" = "false" ]; then
        log_test "Reject Invalid DRL - Syntax Error in Condition" "PASS"
    else
        log_test "Reject Invalid DRL - Syntax Error in Condition" "FAIL" "Status: $status, Valid: $is_valid (expected false)"
    fi
    
    # Validate invalid DRL syntax (negative test) - Missing import
    log_info "Validating invalid DRL - missing import statement..."
    invalid_validate_request='{
        "drlContent": "package rules;\n\nrule \"Missing Import\"\nwhen\n    fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() > 100 )\nthen\n    fact.addViolation(\"ERROR\", \"Missing import\");\nend\n",
        "dataType": "transaction"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$invalid_validate_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    is_valid=$(extract_boolean_field "$body" "valid")
    
    if check_http_status "$response" "200" && [ "$is_valid" = "false" ]; then
        log_test "Reject Invalid DRL - Missing Import" "PASS"
    else
        log_test "Reject Invalid DRL - Missing Import" "FAIL" "Status: $status, Valid: $is_valid (expected false)"
    fi
    
    # Validate invalid DRL syntax (negative test) - Invalid method call
    log_info "Validating invalid DRL - invalid method call..."
    invalid_validate_request='{
        "drlContent": "package rules;\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Invalid Method\"\nwhen\n    fact : DynamicFact( getInvalidMethod(\"amount\") > 100 )\nthen\n    fact.addViolation(\"ERROR\", \"Invalid method\");\nend\n",
        "dataType": "transaction"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$invalid_validate_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    is_valid=$(extract_boolean_field "$body" "valid")
    
    if check_http_status "$response" "200" && [ "$is_valid" = "false" ]; then
        log_test "Reject Invalid DRL - Invalid Method Call" "PASS"
    else
        log_test "Reject Invalid DRL - Invalid Method Call" "FAIL" "Status: $status, Valid: $is_valid (expected false)"
    fi
    
    # Validate invalid DRL syntax (negative test) - Empty DRL content
    log_info "Validating invalid DRL - empty content..."
    invalid_validate_request='{
        "drlContent": "",
        "dataType": "transaction"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$invalid_validate_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    is_valid=$(extract_boolean_field "$body" "valid")
    
    if check_http_status "$response" "200" && [ "$is_valid" = "false" ]; then
        log_test "Reject Invalid DRL - Empty Content" "PASS"
    else
        log_test "Reject Invalid DRL - Empty Content" "FAIL" "Status: $status, Valid: $is_valid (expected false)"
    fi
    
    # Validate invalid DRL syntax (negative test) - Malformed rule structure
    log_info "Validating invalid DRL - malformed rule structure..."
    invalid_validate_request='{
        "drlContent": "package rules;\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Malformed\"\nwhen\n    fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() >\nthen\n    fact.addViolation(\"ERROR\", \"Unclosed bracket\");\nend\n",
        "dataType": "transaction"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$invalid_validate_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    is_valid=$(extract_boolean_field "$body" "valid")
    
    if check_http_status "$response" "200" && [ "$is_valid" = "false" ]; then
        log_test "Reject Invalid DRL - Malformed Rule Structure" "PASS"
    else
        log_test "Reject Invalid DRL - Malformed Rule Structure" "FAIL" "Status: $status, Valid: $is_valid (expected false)"
    fi
    
    # Create rule
    log_info "Creating rule 'High Amount Alert'..."
    local create_request='{
        "name": "High Amount Transaction Alert",
        "description": "Alert on transactions exceeding account balance",
        "dataType": "transaction",
        "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"High Amount Alert\"\nwhen\n    $fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() > getPropertyAsNumber(\"accountBalance\").doubleValue() )\nthen\n    System.out.println(\"ALERT: Transaction amount exceeds account balance!\");\n    $fact.addViolation(\"HIGH_AMOUNT\", \"Transaction amount exceeds account balance\");\nend\n",
        "createdBy": "test-user"
    }'
    
    local response=$(make_request "POST" "$BASE_URL/api/rules" "$create_request" "")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -1)
    export RULE_ID=$(extract_id "$body")
    
    if (check_http_status "$response" "200" || check_http_status "$response" "201") && [ -n "$RULE_ID" ]; then
        log_test "Create Rule" "PASS"
    else
        log_test "Create Rule" "FAIL" "Status: $status, Body: $body"
    fi
    
    # Get all rules
    log_info "Getting all rules..."
    response=$(make_request "GET" "$BASE_URL/api/rules" "" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Get All Rules" "PASS"
    else
        log_test "Get All Rules" "FAIL" "Status: $status"
    fi
    
    # Get rule by ID
    if [ -n "$RULE_ID" ]; then
        log_info "Getting rule by ID..."
        response=$(make_request "GET" "$BASE_URL/api/rules/$RULE_ID" "" "")
        body=$(echo "$response" | head -n -1)
        status=$(echo "$response" | tail -1)
        
        if check_http_status "$response" "200"; then
            log_test "Get Rule by ID" "PASS"
        else
            log_test "Get Rule by ID" "FAIL" "Status: $status"
        fi
    else
        log_test "Get Rule by ID" "FAIL" "No rule ID available"
    fi
    
    # Search rules by data type
    log_info "Searching rules by data type..."
    response=$(make_request "GET" "$BASE_URL/api/rules?dataType=transaction" "" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Search Rules by Data Type" "PASS"
    else
        log_test "Search Rules by Data Type" "FAIL" "Status: $status"
    fi
    
    # Update rule
    if [ -n "$RULE_ID" ]; then
        log_info "Updating rule..."
        local update_request='{
            "name": "Updated High Amount Alert",
            "description": "Updated description",
            "updatedBy": "test-user"
        }'
        
        response=$(make_request "PUT" "$BASE_URL/api/rules/$RULE_ID" "$update_request" "")
        body=$(echo "$response" | head -n -1)
        status=$(echo "$response" | tail -1)
        
        if check_http_status "$response" "200"; then
            log_test "Update Rule" "PASS"
        else
            log_test "Update Rule" "FAIL" "Status: $status"
        fi
        
        # Activate rule
        log_info "Activating rule..."
        response=$(make_request "POST" "$BASE_URL/api/rules/$RULE_ID/activate" "" "")
        body=$(echo "$response" | head -n -1)
        status=$(echo "$response" | tail -1)
        
        if check_http_status "$response" "200"; then
            log_test "Activate Rule" "PASS"
        else
            log_test "Activate Rule" "FAIL" "Status: $status"
        fi
    else
        log_test "Update Rule" "FAIL" "No rule ID available"
        log_test "Activate Rule" "FAIL" "No rule ID available"
    fi
    
    # Get rule template
    log_info "Getting rule template..."
    response=$(make_request "GET" "$BASE_URL/api/rules/example/template" "" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    drl_content=$(extract_value "$body" "drlContent")
    
    # Validate template structure
    if check_http_status "$response" "200" && [ -n "$drl_content" ]; then
        # Check if template contains expected elements
        if echo "$drl_content" | grep -q "package rules;" && \
           echo "$drl_content" | grep -q "import com.frauddetection.domain.DynamicFact;" && \
           echo "$drl_content" | grep -q "rule"; then
            log_test "Get Rule Template" "PASS" "Contains all expected elements"
        else
            log_test "Get Rule Template" "FAIL" "Missing expected template elements"
        fi
    else
        log_test "Get Rule Template" "FAIL" "Status: $status"
    fi
}

# ============================================================================
# CATEGORY 4: Negative Tests (Error Cases)
# ============================================================================
run_negative_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 4: Negative Tests (Error Cases)"
    echo "========================================="
    
    # Create rule with non-existent data type
    log_info "Attempting to create rule with non-existent data type..."
    local create_request='{
        "name": "Invalid Rule",
        "dataType": "non-existent-type",
        "drlContent": "package com.frauddetection.rules;\nrule \"Test\"\nwhen then end\n"
    }'
    
    local response=$(make_request "POST" "$BASE_URL/api/rules" "$create_request" "")
    local status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "400"; then
        log_test "Reject Non-existent Data Type" "PASS"
    else
        log_test "Reject Non-existent Data Type" "FAIL" "Status: $status"
    fi
    
    # Get non-existent rule
    log_info "Attempting to get non-existent rule..."
    response=$(make_request "GET" "$BASE_URL/api/rules/00000000-0000-0000-0000-000000000000" "" "")
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "404"; then
        log_test "Handle Non-existent Rule (404)" "PASS"
    else
        log_test "Handle Non-existent Rule (404)" "FAIL" "Status: $status"
    fi
    
    # Get non-existent data type from data-management-service
    log_info "Attempting to get non-existent data type from data-management-service..."
    response=$(make_request "GET" "$DATA_MANAGEMENT_URL/data-types/nonexistent-type" "" "")
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "404"; then
        log_test "Handle Non-existent Data Type from Data Management Service (404)" "PASS"
    else
        log_test "Handle Non-existent Data Type from Data Management Service (404)" "FAIL" "Status: $status"
    fi
}

# ============================================================================
# CATEGORY 5: Rule Evaluation Tests
# ============================================================================
run_evaluation_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 5: Rule Evaluation Tests"
    echo "========================================="
    
    # Evaluate data
    log_info "Evaluating transaction data..."
    local evaluate_request='{
        "dataType": "transaction",
        "facts": [{
            "amount": 6000.0,
            "accountBalance": 5000.0,
            "type": "debit",
            "paymentMethod": "card"
        }]
    }'
    
    local response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$evaluate_request" "")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Evaluate Data Against Rules" "PASS"
    else
        log_test "Evaluate Data Against Rules" "FAIL" "Status: $status"
    fi
    
    # Evaluate with multiple facts
    log_info "Evaluating multiple facts..."
    evaluate_request='{
        "dataType": "transaction",
        "facts": [
            {
                "amount": 6000.0,
                "accountBalance": 5000.0,
                "type": "debit",
                "paymentMethod": "card"
            },
            {
                "amount": 100.0,
                "accountBalance": 5000.0,
                "type": "debit",
                "paymentMethod": "card"
            }
        ]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$evaluate_request" "")
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Evaluate Multiple Facts" "PASS"
    else
        log_test "Evaluate Multiple Facts" "FAIL" "Status: $status"
    fi
}

# ============================================================================
# CATEGORY 6: Integration Flow Tests
# ============================================================================
run_integration_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 6: Integration Flow Tests"
    echo "========================================="
    
    # Complete workflow test
    log_info "Running complete workflow test..."
    
    # Create a new data type via data-management-service
    local create_dt_request='{
        "data_type": "payment",
        "name": "Payment Data",
        "description": "Payment transaction data",
        "schema_definition": {
            "fields": {
                "amount": "Double",
                "currency": "String",
                "status": "String"
            },
            "required": ["amount"]
        },
        "status": "ACTIVE",
        "created_by": "integration-test"
    }'
    
    local response=$(make_request "POST" "$DATA_MANAGEMENT_URL/data-types" "$create_dt_request" "")
    local dt_status=$(echo "$response" | tail -1)
    local dt_exists
    
    # Data type exists if created (201), updated (200), or already exists (400)
    if check_http_status "$response" "201" || check_http_status "$response" "200" || check_http_status "$response" "400"; then
        dt_exists="true"
    else
        dt_exists="false"
    fi
    
    if [ "$dt_exists" = "true" ]; then
        # Create rule
        local create_rule_request='{
            "name": "Payment Fraud Rule",
            "description": "Detect payment fraud",
            "dataType": "payment",
            "drlContent": "package rules;\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"High Payment Alert\"\nwhen\n    $fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() > 10000 )\nthen\n    $fact.addViolation(\"HIGH_PAYMENT\", \"Payment amount exceeds threshold\");\nend\n",
            "createdBy": "integration-test"
        }'
        
        response=$(make_request "POST" "$BASE_URL/api/rules" "$create_rule_request" "")
        local rule_id=$(extract_id "$(echo "$response" | head -n -1)")
        
        if [ -n "$rule_id" ]; then
            # Activate rule
            response=$(make_request "POST" "$BASE_URL/api/rules/$rule_id/activate" "" "")
            
            # Evaluate
            local eval_request='{
                "dataType": "payment",
                "facts": [{"amount": 15000.0, "currency": "USD", "status": "pending"}]
            }'
            
            response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$eval_request" "")
            
            if check_http_status "$response" "200"; then
                log_test "Complete Workflow Test" "PASS"
            else
                log_test "Complete Workflow Test" "FAIL"
            fi
        else
            log_test "Complete Workflow Test" "FAIL" "Rule creation failed"
        fi
    else
        log_test "Complete Workflow Test" "FAIL" "Data type creation failed or already exists"
    fi
}

# ============================================================================
# CATEGORY 7: Scoring Functional Tests
# ============================================================================
run_scoring_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 7: Scoring Functional Tests"
    echo "========================================="
    
    # Clear database to avoid rule conflicts
    log_info "Clearing database for scoring tests..."
    docker exec fraud-detection-system-postgres-1 psql -U frauduser -d frauddb -c "
        TRUNCATE TABLE rule CASCADE;
    " > /dev/null 2>&1
    
    # Create transaction data type for scoring tests via data-management-service
    log_info "Creating transaction data type for scoring tests via data-management-service..."
    local dt_request='{
        "data_type": "transaction",
        "name": "Transaction Data",
        "description": "Financial transaction data",
        "schema_definition": {
            "fields": {
                "amount": "Double",
                "accountBalance": "Double",
                "type": "String",
                "paymentMethod": "String"
            },
            "required": ["amount", "accountBalance"]
        },
        "status": "ACTIVE",
        "created_by": "scoring-test"
    }'
    
    local response=$(make_request "POST" "$DATA_MANAGEMENT_URL/data-types" "$dt_request" "")
    
    # First, create multiple rules for testing different scenarios
    log_info "Creating multiple rules for scoring tests..."
    
    # Rule 1: High amount alert (triggered when amount > balance) - use unique name
    local rule1_request='{
        "name": "Scoring High Amount Alert",
        "description": "Alert when transaction amount exceeds balance",
        "dataType": "transaction",
        "drlContent": "package rules;\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"ScoringHighAmountAlert\"\nwhen\n    $fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() > getPropertyAsNumber(\"accountBalance\").doubleValue() )\nthen\n    $fact.addViolation(\"HIGH_AMOUNT\", \"Transaction exceeds balance\", 5);\nend\n",
        "createdBy": "scoring-test"
    }'
    
    local response=$(make_request "POST" "$BASE_URL/api/rules" "$rule1_request" "")
    local rule1_id=$(extract_id "$(echo "$response" | head -n -1)")
    
    if [ -n "$rule1_id" ]; then
        make_request "POST" "$BASE_URL/api/rules/$rule1_id/activate" "" "" > /dev/null 2>&1
    fi
    
    # Rule 2: Suspicious payment method - use unique name
    local rule2_request='{
        "name": "Scoring Suspicious Payment Method",
        "description": "Alert on suspicious payment methods",
        "dataType": "transaction",
        "drlContent": "package rules;\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"ScoringSuspiciousPaymentMethod\"\nwhen\n    $fact : DynamicFact( getPropertyAsString(\"paymentMethod\").equals(\"cryptocurrency\") )\nthen\n    $fact.addViolation(\"SUSPICIOUS_METHOD\", \"Cryptocurrency payment detected\", 3);\nend\n",
        "createdBy": "scoring-test"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules" "$rule2_request" "")
    local rule2_id=$(extract_id "$(echo "$response" | head -n -1)")
    
    if [ -n "$rule2_id" ]; then
        make_request "POST" "$BASE_URL/api/rules/$rule2_id/activate" "" "" > /dev/null 2>&1
    fi
    
    # Rule 3: Multiple violations threshold - use unique name
    local rule3_request='{
        "name": "Scoring Unusual Transaction Alert",
        "description": "Alert when transaction type is unusual",
        "dataType": "transaction",
        "drlContent": "package rules;\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"ScoringUnusualTransactionType\"\nwhen\n    $fact : DynamicFact( getPropertyAsString(\"type\").equals(\"wire_transfer\") )\nthen\n    $fact.addViolation(\"UNUSUAL_TYPE\", \"Wire transfer detected\", 2);\nend\n",
        "createdBy": "scoring-test"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules" "$rule3_request" "")
    local rule3_id=$(extract_id "$(echo "$response" | head -n -1)")
    
    if [ -n "$rule3_id" ]; then
        make_request "POST" "$BASE_URL/api/rules/$rule3_id/activate" "" "" > /dev/null 2>&1
    fi
    
    # Test 1: Zero violations - should have score 0
    echo ""
    log_info "Test 1: Zero violations (normal transaction)..."
    local test1_request='{
        "dataType": "transaction",
        "facts": [{
            "amount": 100.0,
            "accountBalance": 5000.0,
            "type": "debit",
            "paymentMethod": "card"
        }]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test1_request" "")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -1)
    local score=$(extract_value "$body" "riskScore")
    
    echo "  Score: $score"
    # Use numeric comparison that handles both 0 and 0.0
    local numeric_score=$(echo "$score" | awk '{print int($1)}' 2>/dev/null)
    if check_http_status "$response" "200" && [ "$numeric_score" = "0" ]; then
        log_test "Zero Violations Score" "PASS" "Score: $score"
    else
        log_test "Zero Violations Score" "FAIL" "Expected 0, got: $score"
    fi
    
    # Test 2: Single violation - should have score = violation weight
    echo ""
    log_info "Test 2: Single violation (high amount)..."
    local test2_request='{
        "dataType": "transaction",
        "facts": [{
            "amount": 6000.0,
            "accountBalance": 5000.0,
            "type": "debit",
            "paymentMethod": "card"
        }]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test2_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    score=$(extract_value "$body" "riskScore")
    local violations_count=$(extract_value "$body" "violationsCount")
    
    echo "  Score: $score, Violations: $violations_count"
    # Use awk for numeric comparison that handles decimal values
    if check_http_status "$response" "200" && [ "$violations_count" = "1" ] && [ "$(echo "$score" | awk '{print ($1 > 0)}' 2>/dev/null)" = "1" ]; then
        log_test "Single Violation Score" "PASS" "Score: $score, Violations: $violations_count"
    else
        log_test "Single Violation Score" "FAIL" "Score: $score, Violations: $violations_count"
    fi
    
    # Test 3: Multiple violations - cumulative score
    echo ""
    log_info "Test 3: Multiple violations (high amount + suspicious method)..."
    local test3_request='{
        "dataType": "transaction",
        "facts": [{
            "amount": 6000.0,
            "accountBalance": 5000.0,
            "type": "debit",
            "paymentMethod": "cryptocurrency"
        }]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test3_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    score=$(extract_value "$body" "riskScore")
    violations_count=$(extract_value "$body" "violationsCount")
    
    echo "  Score: $score, Violations: $violations_count"
    # Should have at least 2 violations (high amount + suspicious method)
    if check_http_status "$response" "200" && [ "$violations_count" -ge "2" ]; then
        log_test "Multiple Violations Cumulative Score" "PASS" "Score: $score, Violations: $violations_count"
    else
        log_test "Multiple Violations Cumulative Score" "FAIL" "Score: $score, Violations: $violations_count"
    fi
    
    # Test 4: Partial rule match (only some rules trigger)
    echo ""
    log_info "Test 4: Partial rule match (unusual type only)..."
    local test4_request='{
        "dataType": "transaction",
        "facts": [{
            "amount": 100.0,
            "accountBalance": 5000.0,
            "type": "wire_transfer",
            "paymentMethod": "card"
        }]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test4_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    score=$(extract_value "$body" "riskScore")
    violations_count=$(extract_value "$body" "violationsCount")
    
    echo "  Score: $score, Violations: $violations_count"
    # Should have 1 violation (unusual type)
    if check_http_status "$response" "200" && [ "$violations_count" -ge "1" ]; then
        log_test "Partial Rule Match Score" "PASS" "Score: $score, Violations: $violations_count"
    else
        log_test "Partial Rule Match Score" "FAIL" "Score: $score, Violations: $violations_count"
    fi
    
    # Test 5: Multiple facts with different outcomes
    echo ""
    log_info "Test 5: Multiple facts with mixed outcomes (average score)..."
    local test5_request='{
        "dataType": "transaction",
        "facts": [
            {
                "amount": 100.0,
                "accountBalance": 5000.0,
                "type": "debit",
                "paymentMethod": "card"
            },
            {
                "amount": 6000.0,
                "accountBalance": 5000.0,
                "type": "debit",
                "paymentMethod": "cryptocurrency"
            },
            {
                "amount": 50.0,
                "accountBalance": 5000.0,
                "type": "wire_transfer",
                "paymentMethod": "card"
            }
        ]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test5_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    score=$(extract_value "$body" "riskScore")
    violations_count=$(extract_value "$body" "violationsCount")
    local metadata=$(extract_value "$body" "metadata")
    
    echo "  Average Score: $score, Total Violations: $violations_count"
    echo "  Metadata: $metadata"
    if check_http_status "$response" "200" && [ "$(echo "$score" | awk '{print ($1 > 0)}' 2>/dev/null)" = "1" ]; then
        log_test "Multiple Facts Average Score" "PASS" "Average Score: $score"
    else
        log_test "Multiple Facts Average Score" "FAIL" "Score: $score"
    fi
    
    # Test 6: Edge case - very high amount
    echo ""
    log_info "Test 6: Edge case - very high transaction amount..."
    local test6_request='{
        "dataType": "transaction",
        "facts": [{
            "amount": 1000000.0,
            "accountBalance": 5000.0,
            "type": "debit",
            "paymentMethod": "card"
        }]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test6_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    score=$(extract_value "$body" "riskScore")
    violations_count=$(extract_value "$body" "violationsCount")
    
    echo "  Score: $score, Violations: $violations_count"
    if check_http_status "$response" "200" && [ "$violations_count" -ge "1" ]; then
        log_test "Edge Case High Amount" "PASS" "Score: $score"
    else
        log_test "Edge Case High Amount" "FAIL" "Score: $score"
    fi
    
    # Test 7: All violations triggered simultaneously
    echo ""
    log_info "Test 7: All rules triggered (maximum violations)..."
    local test7_request='{
        "dataType": "transaction",
        "facts": [{
            "amount": 1000000.0,
            "accountBalance": 1000.0,
            "type": "wire_transfer",
            "paymentMethod": "cryptocurrency"
        }]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test7_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    score=$(extract_value "$body" "riskScore")
    violations_count=$(extract_value "$body" "violationsCount")
    local violations=$(echo "$body" | jq -r '.violations[]' 2>/dev/null)
    
    echo "  Score: $score, Violations: $violations_count"
    if check_http_status "$response" "200" && [ "$violations_count" -ge "3" ]; then
        log_test "Maximum Violations Score" "PASS" "Score: $score, Total Violations: $violations_count"
    else
        log_test "Maximum Violations Score" "FAIL" "Score: $score, Violations: $violations_count"
    fi
    
    # Test 8: Verify score consistency with different fact combinations
    echo ""
    log_info "Test 8: Score consistency verification..."
    local test8a_request='{
        "dataType": "transaction",
        "facts": [{"amount": 6000.0, "accountBalance": 5000.0, "type": "debit", "paymentMethod": "card"}]
    }'
    
    local test8b_request='{
        "dataType": "transaction",
        "facts": [{"amount": 6000.0, "accountBalance": 5000.0, "type": "debit", "paymentMethod": "card"}]
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test8a_request" "")
    local score1=$(echo "$response" | head -n -1 | jq -r '.riskScore' 2>/dev/null)
    
    response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$test8b_request" "")
    local score2=$(echo "$response" | head -n -1 | jq -r '.riskScore' 2>/dev/null)
    
    echo "  Score 1: $score1, Score 2: $score2"
    # Compare using awk for numeric comparison
    if [ "$(awk -v a="$score1" -v b="$score2" 'BEGIN {print (a == b)}' 2>/dev/null)" = "1" ] || [ "$score1" = "$score2" ]; then
        log_test "Score Consistency" "PASS" "Both scores match: $score1"
    else
        log_test "Score Consistency" "FAIL" "Scores differ: $score1 vs $score2"
    fi
}

# ============================================================================
# CATEGORY 8: Data Management Integration Tests
# ============================================================================
run_data_management_integration_tests() {
    echo ""
    echo "========================================="
    echo "CATEGORY 8: Data Management Integration Tests"
    echo "========================================="
    
    # Test 1: Create data type in data-management-service
    echo ""
    log_info "Test 1: Creating data type in data-management-service..."
    local create_dt_request='{
        "data_type": "fraud_test_transaction",
        "name": "Fraud Test Transaction",
        "description": "Transaction data for fraud testing",
        "schema_definition": {
            "fields": {
                "amount": "Double",
                "accountBalance": "Double",
                "type": "String",
                "paymentMethod": "String",
                "merchantName": "String",
                "timestamp": "String"
            },
            "required": ["amount", "accountBalance"]
        },
        "sample_data": {
            "amount": 1000.0,
            "accountBalance": 5000.0,
            "type": "debit",
            "paymentMethod": "card",
            "merchantName": "Test Merchant",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        "status": "ACTIVE",
        "created_by": "integration-test"
    }'
    
    local response=$(make_request "POST" "$DATA_MANAGEMENT_URL/data-types" "$create_dt_request" "")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -1)
    local data_type_id=$(echo "$body" | jq -r '.data_type' 2>/dev/null)
    
    if check_http_status "$response" "201" || check_http_status "$response" "200"; then
        log_test "Create Data Type in Data Management Service" "PASS"
    elif check_http_status "$response" "400"; then
        # Data type already exists, that's OK for this test
        log_test "Create Data Type in Data Management Service" "PASS" "(already exists)"
    else
        log_test "Create Data Type in Data Management Service" "FAIL" "Status: $status"
        return  # Skip remaining tests if this fails
    fi
    
    # Test 2: Verify data type exists
    echo ""
    log_info "Test 2: Verifying data type exists in data-management-service..."
    response=$(make_request "GET" "$DATA_MANAGEMENT_URL/data-types/fraud_test_transaction" "" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Verify Data Type Exists" "PASS"
    else
        log_test "Verify Data Type Exists" "FAIL" "Status: $status"
    fi
    
    # Test 3: Create rule referencing the new data type
    echo ""
    log_info "Test 3: Creating rule for the new data type..."
    local create_rule_request='{
        "name": "Fraud Test Rule",
        "description": "Detect suspicious merchant transactions",
        "dataType": "fraud_test_transaction",
        "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Suspicious Merchant Alert\"\nwhen\n    $fact : DynamicFact( getPropertyAsNumber(\"amount\").doubleValue() > 10000 )\nthen\n    $fact.addViolation(\"SUSPICIOUS_MERCHANT\", \"High amount merchant transaction\", 4);\nend\n",
        "createdBy": "integration-test"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules" "$create_rule_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    local rule_id=$(extract_id "$body")
    
    if check_http_status "$response" "200" && [ -n "$rule_id" ]; then
        log_test "Create Rule with Data Type from Data Management Service" "PASS"
    else
        log_test "Create Rule with Data Type from Data Management Service" "FAIL" "Status: $status"
    fi
    
    # Test 4: Attempt to create rule with non-existent data type
    echo ""
    log_info "Test 4: Attempting to create rule with non-existent data type..."
    local invalid_rule_request='{
        "name": "Invalid Rule",
        "description": "This should fail",
        "dataType": "nonexistent_type_xyz123",
        "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Invalid\"\nwhen\n    $fact : DynamicFact( getPropertyAsString(\"type\").equals(\"test\") )\nthen\n    $fact.addViolation(\"ERROR\", \"This should fail\");\nend\n",
        "createdBy": "integration-test"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules" "$invalid_rule_request" "")
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "400"; then
        log_test "Reject Rule Creation with Non-existent Data Type" "PASS"
    else
        log_test "Reject Rule Creation with Non-existent Data Type" "FAIL" "Status: $status (expected 400)"
    fi
    
    # Test 5: Test schema validation - field mismatch
    echo ""
    log_info "Test 5: Testing schema validation with invalid field name..."
    local invalid_field_rule_request='{
        "name": "Invalid Field Rule",
        "description": "Rule with invalid field reference",
        "dataType": "fraud_test_transaction",
        "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Invalid Field Alert\"\nwhen\n    $fact : DynamicFact( getPropertyAsNumber(\"invalidField123\").doubleValue() > 100 )\nthen\n    $fact.addViolation(\"INVALID\", \"Invalid field reference\");\nend\n",
        "createdBy": "integration-test"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules" "$invalid_field_rule_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "400"; then
        log_test "Reject Rule with Invalid Field Name" "PASS"
    else
        log_test "Reject Rule with Invalid Field Name" "FAIL" "Status: $status (expected 400)"
    fi
    
    # Test 6: Test schema validation - valid field names
    echo ""
    log_info "Test 6: Creating rule with valid field names from schema..."
    local valid_field_rule_request='{
        "name": "Valid Field Rule",
        "description": "Rule with valid field references",
        "dataType": "fraud_test_transaction",
        "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Valid Field Alert\"\nwhen\n    $fact : DynamicFact( getPropertyAsString(\"merchantName\").equals(\"Suspicious Merchant\") )\nthen\n    $fact.addViolation(\"SUSPICIOUS_MERCHANT\", \"Known suspicious merchant\", 5);\nend\n",
        "createdBy": "integration-test"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules" "$valid_field_rule_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    local valid_rule_id=$(extract_id "$body")
    
    if check_http_status "$response" "200" && [ -n "$valid_rule_id" ]; then
        log_test "Accept Rule with Valid Field Names" "PASS"
    else
        log_test "Accept Rule with Valid Field Names" "FAIL" "Status: $status"
    fi
    
    # Test 7: Activate rule and evaluate
    if [ -n "$valid_rule_id" ]; then
        echo ""
        log_info "Test 7: Activating rule and evaluating data..."
        
        # Activate rule
        response=$(make_request "POST" "$BASE_URL/api/rules/$valid_rule_id/activate" "" "")
        status=$(echo "$response" | tail -1)
        
        if check_http_status "$response" "200"; then
            log_test "Activate Rule for Evaluation" "PASS"
            
            # Evaluate with test data
            local eval_request='{
                "dataType": "fraud_test_transaction",
                "facts": [{
                    "amount": 5000.0,
                    "accountBalance": 10000.0,
                    "type": "debit",
                    "paymentMethod": "card",
                    "merchantName": "Suspicious Merchant",
                    "timestamp": "2024-01-01T10:00:00Z"
                }]
            }'
            
            response=$(make_request "POST" "$BASE_URL/api/evaluate/" "$eval_request" "")
            status=$(echo "$response" | tail -1)
            
            if check_http_status "$response" "200"; then
                log_test "Evaluate Data with Data Type from Data Management Service" "PASS"
            else
                log_test "Evaluate Data with Data Type from Data Management Service" "FAIL" "Status: $status"
            fi
        else
            log_test "Activate Rule for Evaluation" "FAIL" "Status: $status"
        fi
    fi
    
    # Test 8: Get schema information
    echo ""
    log_info "Test 8: Getting schema information for validation..."
    response=$(make_request "GET" "$DATA_MANAGEMENT_URL/data-types/fraud_test_transaction" "" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    
    # Check if the response contains schema_definition field (indicates valid response)
    local has_schema=$(echo "$body" | grep -o "schema_definition" 2>/dev/null)
    
    if check_http_status "$response" "200" && [ -n "$has_schema" ]; then
        log_test "Get Schema Information for Validation" "PASS"
    else
        log_test "Get Schema Information for Validation" "FAIL" "Status: $status"
    fi
    
    # Test 9: Update data type and verify rule still works
    echo ""
    log_info "Test 9: Updating data type schema..."
    local update_dt_request='{
        "description": "Updated transaction data for fraud testing",
        "schema_definition": {
            "fields": {
                "amount": "Double",
                "accountBalance": "Double",
                "type": "String",
                "paymentMethod": "String",
                "merchantName": "String",
                "timestamp": "String",
                "riskLevel": "String"
            },
            "required": ["amount", "accountBalance"]
        },
        "status": "ACTIVE"
    }'
    
    response=$(make_request "PUT" "$DATA_MANAGEMENT_URL/data-types/fraud_test_transaction" "$update_dt_request" "")
    status=$(echo "$response" | tail -1)
    
    if check_http_status "$response" "200"; then
        log_test "Update Data Type Schema" "PASS"
    else
        log_test "Update Data Type Schema" "FAIL" "Status: $status"
    fi
    
    # Test 10: Validate DRL using schema from data-management-service
    echo ""
    log_info "Test 10: Validating DRL against schema from data-management-service..."
    local validate_request='{
        "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"Risk Level Check\"\nwhen\n    $fact : DynamicFact( getPropertyAsString(\"riskLevel\").equals(\"high\") )\nthen\n    $fact.addViolation(\"HIGH_RISK\", \"High risk transaction\", 8);\nend\n",
        "dataType": "fraud_test_transaction"
    }'
    
    response=$(make_request "POST" "$BASE_URL/api/rules/validate" "$validate_request" "")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -1)
    local is_valid=$(extract_boolean_field "$body" "valid")
    
    if check_http_status "$response" "200" && [ "$is_valid" = "true" ]; then
        log_test "Validate DRL Against Schema from Data Management Service" "PASS"
    else
        log_test "Validate DRL Against Schema from Data Management Service" "FAIL" "Status: $status, Valid: $is_valid"
    fi
}

# ============================================================================
# Main Execution
# ============================================================================
main() {
    echo ""
    echo "========================================="
    echo "Rule Engine Service - Workflow Tests"
    echo "========================================="
    echo ""
    echo "Starting tests at $(date)"
    echo "Testing service at: $BASE_URL"
    
    # Clear database before running tests
    clear_database
    
    run_health_tests
    run_data_type_tests
    run_rule_tests
    run_evaluation_tests
    run_negative_tests
    run_integration_tests
    run_scoring_tests
    run_data_management_integration_tests
    
    # Print summary
    echo ""
    echo "========================================="
    echo "Test Summary"
    echo "========================================="
    echo "Total Tests: $((TEST_PASSED + TEST_FAILED))"
    echo -e "${GREEN}Passed: $TEST_PASSED${NC}"
    echo -e "${RED}Failed: $TEST_FAILED${NC}"
    
    if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
        echo ""
        echo "Failed tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
    fi
    
    echo ""
    echo "Tests completed at $(date)"
    echo "========================================="
    
    # Exit with appropriate code
    [ $TEST_FAILED -eq 0 ]
}

# Run main
main

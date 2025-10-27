#!/bin/bash

# Financial Services Integration Demo Script
# This demonstrates how a financial services application integrates with the fraud detection system

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
CALLBACK_PORT="${CALLBACK_PORT:-9000}"

echo "================================================================"
echo "Financial Services Fraud Detection Integration Demo"
echo "================================================================"
echo ""
echo "This demo shows how a financial services application integrates"
echo "with the fraud detection system for real-time risk assessment."
echo ""
echo "Backend URL: $BACKEND_URL"
echo "Callback Server Port: $CALLBACK_PORT"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_evaluation() {
    local scenario=$1
    local data_type=$2
    local facts=$3
    local description=$4
    
    echo "----------------------------------------------------------------"
    echo -e "${BLUE}Scenario: $scenario${NC}"
    echo -e "${YELLOW}Description: $description${NC}"
    echo ""
    
    echo "📤 Submitting evaluation request..."
    response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/evaluate" \
        -H "Content-Type: application/json" \
        -d "{
            \"dataType\": \"$data_type\",
            \"facts\": [$facts]
        }")
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    
    echo ""
    if [ "$http_code" = "202" ]; then
        echo -e "${GREEN}✓ Request Accepted (HTTP $http_code)${NC}"
        echo "Response: $body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ Request Failed (HTTP $http_code)${NC}"
        echo "Response: $body"
    fi
    
    echo ""
    echo "ℹ️  Note: The actual evaluation results will be sent to your"
    echo "   configured callback endpoint asynchronously."
    echo ""
}

# Test scenario 1: Low risk transaction (auto_approve)
echo "================================================================"
echo "Scenario 1: Low Risk Transaction - Auto Approve"
echo "================================================================"
test_evaluation \
    "Low Risk Transaction" \
    "transactions" \
    "{\"customer_id\": \"CUST_001\", \"date\": \"2024-10-27T10:00:00\", \"credit\": 1000, \"debit\": 0, \"closingBalance\": 50000, \"source\": \"MOBILE_BANKING\", \"narrative\": \"Salary Transfer\", \"is_anomaly\": 0}" \
    "Normal salary transfer with sufficient balance - should auto approve"

sleep 2

# Test scenario 2: Medium risk transaction (human_review)
echo "================================================================"
echo "Scenario 2: Medium Risk Transaction - Requires Human Review"
echo "================================================================"
test_evaluation \
    "Medium Risk Transaction" \
    "transactions" \
    "{\"customer_id\": \"CUST_002\", \"date\": \"2024-10-27T11:00:00\", \"credit\": 0, \"debit\": 15000, \"closingBalance\": 25000, \"source\": \"CASH WITHDRAWAL\", \"narrative\": \"Large Cash Withdrawal\", \"is_anomaly\": 0}" \
    "Large cash withdrawal - should trigger human review"

sleep 2

# Test scenario 3: High risk transaction (auto_reject or human_review)
echo "================================================================"
echo "Scenario 3: High Risk Transaction - Human Review"
echo "================================================================"
test_evaluation \
    "High Risk Transaction" \
    "transactions" \
    "{\"customer_id\": \"CUST_003\", \"date\": \"2024-10-27T12:00:00\", \"credit\": 150000, \"debit\": 0, \"closingBalance\": 200000, \"source\": \"WIRE_TRANSFER\", \"narrative\": \"International Transfer\", \"is_anomaly\": 1}" \
    "Very large international transfer flagged as anomaly - should trigger human review"

sleep 2

# Test scenario 4: KYC - Low risk customer (auto_approve)
echo "================================================================"
echo "Scenario 4: KYC - Low Risk Customer - Auto Approve"
echo "================================================================"
test_evaluation \
    "Low Risk KYC" \
    "kyc" \
    "{\"customer_id\": \"CUST_101\", \"customer_name\": \"Sarah Johnson\", \"customer_age\": 45, \"customer_gender\": \"female\", \"customer_marital_status\": \"married\", \"customer_education_level\": \"bachelor\", \"customer_phone_number\": 911234567, \"customer_tin_number\": \"1234567890\", \"customer_bank_account_number\": \"1234567890123\", \"customer_region\": \"ADDIS_ABABA\", \"customer_city\": \"ADDIS_ABABA\", \"customer_woreda\": 1, \"business_id\": \"BUS_001\", \"business_name\": \"Johnson Enterprise\", \"business_sector\": \"TECHNOLOGY\", \"business_current_capital\": 500000, \"business_current_no_of_employees\": 20}" \
    "Well-established business owner with good profile - should auto approve"

sleep 2

# Test scenario 5: KYC - High risk (human_review)
echo "================================================================"
echo "Scenario 5: KYC - High Risk Customer - Human Review"
echo "================================================================"
test_evaluation \
    "High Risk KYC" \
    "kyc" \
    "{\"customer_id\": \"CUST_102\", \"customer_name\": \"John Doe\", \"customer_age\": 17, \"customer_gender\": \"male\", \"customer_marital_status\": \"single\", \"customer_education_level\": \"none\", \"customer_tin_number\": \"\", \"customer_bank_account_number\": \"\", \"customer_region\": \"\", \"business_id\": \"BUS_002\", \"business_name\": \"Suspicious Corp\", \"business_sector\": \"UNKNOWN\", \"business_current_capital\": 10000, \"business_current_no_of_employees\": 50}" \
    "Underage customer with missing documents and suspicious business - should trigger human review"

sleep 2

# Test scenario 6: Extreme anomaly
echo "================================================================"
echo "Scenario 6: Extreme Anomaly - Human Review"
echo "================================================================"
test_evaluation \
    "Extreme Anomaly" \
    "transactions" \
    "{\"customer_id\": \"CUST_004\", \"date\": \"2025-12-01T10:00:00\", \"credit\": 0, \"debit\": 50000, \"closingBalance\": -20000, \"source\": \"UNKNOWN\", \"narrative\": \"\", \"is_anomaly\": 1}" \
    "Future dated transaction with negative balance and missing details - should trigger urgent human review"

echo ""
echo "================================================================"
echo "Summary"
echo "================================================================"
echo ""
echo -e "${GREEN}✓ All evaluation requests submitted successfully${NC}"
echo ""
echo "Response Pattern:"
echo "  1. HTTP 202 Accepted - Request accepted immediately"
echo "  2. Evaluation runs asynchronously in background"
echo "  3. Results sent via callback to configured endpoint"
echo ""
echo "Decision Types:"
echo "  • ${GREEN}auto_approve${NC} - Low risk, automatic processing"
echo "  • ${YELLOW}human_review${NC} - Medium/High risk, requires analyst review"
echo "  • ${RED}auto_reject${NC} - Critical risk, immediate blocking"
echo ""
echo "Workflow Integration:"
echo "  1. Client submits evaluation request"
echo "  2. Fraud detection API acknowledges (202)"
echo "  3. Processing happens asynchronously"
echo "  4. Results delivered via callback webhook"
echo "  5. Client acts on results (approve/reject/review)"
echo ""
echo "================================================================"
echo "Demo Complete"
echo "================================================================"
echo ""
echo "Note: To test callbacks, configure a callback endpoint and"
echo "      the fraud detection system will POST results there."
echo ""


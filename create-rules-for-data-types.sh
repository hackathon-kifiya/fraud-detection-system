#!/bin/bash

# Script to create rules for each data type in the fraud detection system
# This script creates comprehensive rules for KYC and Transactions data types

set -e

RULE_ENGINE_URL="${RULE_ENGINE_URL:-http://localhost:8081}"
echo "Creating rules for all data types..."
echo "Rule Engine URL: $RULE_ENGINE_URL"

# Function to create a rule using Python for proper JSON escaping
create_rule() {
    local name="$1"
    local data_type="$2"
    local description="$3"
    local drl_content="$4"
    local status="${5:-ACTIVE}"
    local created_by="${6:-system}"
    
    local response=$(python3 << PYEOF
import json
import sys

try:
    payload = {
        "name": "$name",
        "dataType": "$data_type",
        "status": "$status",
        "drlContent": """$drl_content""",
        "description": "$description",
        "createdBy": "$created_by"
    }
    print(json.dumps(payload))
except Exception as e:
    print(f"Error creating payload: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
)
    
    echo "Creating rule: $name for data type: $data_type"
    curl -X POST "$RULE_ENGINE_URL/api/rules" \
        -H "Content-Type: application/json" \
        -d "$response" | python3 -m json.tool || echo "Failed to create rule: $name"
    echo ""
}

echo "========================================="
echo "Creating KYC Data Type Rules"
echo "========================================="

# KYC Rule 1: High Risk Customer Age
create_rule \
    "KYC High Risk Customer Age" \
    "kyc" \
    "Flags customers under 18 years of age which may indicate fraud or ineligibility" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"High Risk Customer Age\"
    when
        \$fact : DynamicFact( getPropertyAsNumber(\"customer_age\").intValue() < 18 )
    then
        \$fact.addViolation(\"INVALID_CUSTOMER_AGE\", \"Customer age is below legal minimum (18 years)\", 8);
        System.out.println(\"ALERT: High risk customer age detected!\");
end" \
    "ACTIVE" \
    "system"

# KYC Rule 2: Missing Customer Identification
create_rule \
    "KYC Missing Customer Identification" \
    "kyc" \
    "Flags missing or invalid customer identification fields" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Missing Customer TIN\"
    when
        \$fact : DynamicFact( !hasProperty(\"customer_tin_number\") || getPropertyAsString(\"customer_tin_number\").isEmpty() )
    then
        \$fact.addViolation(\"MISSING_CUSTOMER_TIN\", \"Customer TIN number is missing or invalid\", 5);
end

rule \"Missing Bank Account\"
    when
        \$fact : DynamicFact( !hasProperty(\"customer_bank_account_number\") || getPropertyAsString(\"customer_bank_account_number\").isEmpty() )
    then
        \$fact.addViolation(\"MISSING_BANK_ACCOUNT\", \"Customer bank account number is missing or invalid\", 4);
end" \
    "ACTIVE" \
    "system"

# KYC Rule 3: Suspicious Business Profile
create_rule \
    "KYC Suspicious Business Profile" \
    "kyc" \
    "Flags businesses with low capital relative to employee count or high suspicious activity indicators" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Suspicious Employee to Capital Ratio\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"business_current_no_of_employees\").intValue() > 10 && 
            getPropertyAsNumber(\"business_current_capital\").doubleValue() < 50000
        )
    then
        \$fact.addViolation(\"SUSPICIOUS_EMPLOYEE_RATIO\", \"High employee count with low capital may indicate fraud\", 7);
        System.out.println(\"ALERT: Suspicious business employee to capital ratio detected!\");
end

rule \"Low Business Sales\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"business_current_capital\").doubleValue() > 100000 &&
            getPropertyAsNumber(\"business_annual_sales\").doubleValue() < 10000
        )
    then
        \$fact.addViolation(\"LOW_BUSINESS_SALES\", \"High capital but very low sales may indicate money laundering\", 6);
end" \
    "ACTIVE" \
    "system"

# KYC Rule 4: Geographic Risk Assessment
create_rule \
    "KYC Geographic Risk Assessment" \
    "kyc" \
    "Flags customers or businesses in high-risk geographic areas" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Incomplete Geographic Information\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"customer_region\") || 
            !hasProperty(\"customer_city\") || 
            !hasProperty(\"customer_woreda\")
        )
    then
        \$fact.addViolation(\"INCOMPLETE_GEOGRAPHIC_INFO\", \"Missing geographic location information\", 3);
end" \
    "ACTIVE" \
    "system"

# KYC Rule 5: Customer Education and Employment Validation
create_rule \
    "KYC Education and Employment Validation" \
    "kyc" \
    "Validates customer education level and employment information for risk assessment" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Missing Education Information\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"customer_education_level\") || 
            getPropertyAsString(\"customer_education_level\").isEmpty()
        )
    then
        \$fact.addViolation(\"MISSING_EDUCATION\", \"Customer education level is missing\", 2);
end

rule \"Missing Marital Status\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"customer_marital_status\") || 
            getPropertyAsString(\"customer_marital_status\").isEmpty()
        )
    then
        \$fact.addViolation(\"MISSING_MARITAL_STATUS\", \"Customer marital status is missing\", 2);
end" \
    "ACTIVE" \
    "system"

# KYC Rule 6: Business Capital and Performance Analysis
create_rule \
    "KYC Business Performance Analysis" \
    "kyc" \
    "Analyzes business capital, profit, and growth patterns for fraud indicators" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Suspicious Profit Margin\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"business_annual_sales\").doubleValue() > 0 &&
            getPropertyAsNumber(\"business_annual_profit\").doubleValue() > getPropertyAsNumber(\"business_annual_sales\").doubleValue()
        )
    then
        \$fact.addViolation(\"SUSPICIOUS_PROFIT_MARGIN\", \"Profit exceeds sales - impossible scenario\", 9);
        System.out.println(\"ALERT: Impossible profit margin detected!\");
end

rule \"Capital Decrease Alarm\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"business_current_capital\").doubleValue() < getPropertyAsNumber(\"business_starting_capital\").doubleValue() * 0.5
        )
    then
        \$fact.addViolation(\"CAPITAL_DECREASE\", \"Business capital decreased significantly (more than 50%)\", 5);
end

rule \"Unrealistic Employee Growth\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"business_current_no_of_employees\").intValue() < getPropertyAsNumber(\"business_starting_no_of_employees\").intValue()
        )
    then
        \$fact.addViolation(\"EMPLOYEE_DECLINE\", \"Employee count decreased (potential business decline)\", 4);
end" \
    "ACTIVE" \
    "system"

# KYC Rule 7: Business Establishment and Compliance
create_rule \
    "KYC Business Compliance Checks" \
    "kyc" \
    "Validates business establishment details and compliance requirements" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Very New Business\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"business_establishment_year\").intValue() > 2022
        )
    then
        \$fact.addViolation(\"VERY_NEW_BUSINESS\", \"Business established less than 2 years ago - higher risk\", 3);
end

rule \"Missing Business TIN\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"business_tin_number\") || 
            getPropertyAsString(\"business_tin_number\").isEmpty()
        )
    then
        \$fact.addViolation(\"MISSING_BUSINESS_TIN\", \"Business TIN number is missing\", 6);
end

rule \"Missing Business Sector\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"business_sector\") || 
            getPropertyAsString(\"business_sector\").isEmpty()
        )
    then
        \$fact.addViolation(\"MISSING_BUSINESS_SECTOR\", \"Business sector information is missing\", 3);
end" \
    "ACTIVE" \
    "system"

# KYC Rule 8: Contact and Identity Verification
create_rule \
    "KYC Contact and Identity Verification" \
    "kyc" \
    "Validates customer contact information and phone numbers" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Invalid Phone Number Format\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"customer_phone_number\").doubleValue() < 900000000 ||
            getPropertyAsNumber(\"customer_phone_number\").doubleValue() > 999999999
        )
    then
        \$fact.addViolation(\"INVALID_PHONE\", \"Customer phone number appears invalid\", 4);
end

rule \"Missing Customer Name\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"customer_name\") || 
            getPropertyAsString(\"customer_name\").trim().length() < 3
        )
    then
        \$fact.addViolation(\"MISSING_CUSTOMER_NAME\", \"Customer name is missing or too short\", 7);
end

rule \"Duplicate Customer ID\"
    when
        \$fact : DynamicFact( 
            getPropertyAsString(\"customer_id\").isEmpty() || 
            getPropertyAsString(\"customer_id\").length() < 3
        )
    then
        \$fact.addViolation(\"INVALID_CUSTOMER_ID\", \"Customer ID is missing or invalid\", 6);
end" \
    "ACTIVE" \
    "system"

# KYC Rule 9: Business Location Validation
create_rule \
    "KYC Business Location Validation" \
    "kyc" \
    "Validates business location information and compares with customer location" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Mismatched Business Location\"
    when
        \$fact : DynamicFact( 
            hasProperty(\"business_city\") && 
            hasProperty(\"customer_city\") &&
            !getPropertyAsString(\"business_city\").equals(getPropertyAsString(\"customer_city\"))
        )
    then
        \$fact.addViolation(\"LOCATION_MISMATCH\", \"Business and customer are in different cities\", 4);
end

rule \"Missing Business Location\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"business_city\") || 
            getPropertyAsString(\"business_city\").isEmpty()
        )
    then
        \$fact.addViolation(\"MISSING_BUSINESS_LOCATION\", \"Business city is missing\", 4);
end" \
    "ACTIVE" \
    "system"

echo ""
echo "========================================="
echo "Creating Transaction Data Type Rules"
echo "========================================="

# Transaction Rule 1: High Value Transaction
create_rule \
    "Transaction High Value Alert" \
    "transactions" \
    "Flags high-value transactions that exceed normal thresholds" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"High Value Credit Transaction\"
    when
        \$fact : DynamicFact( getPropertyAsNumber(\"credit\").doubleValue() > 50000.0 )
    then
        \$fact.addViolation(\"HIGH_VALUE_CREDIT\", \"Credit transaction exceeds 50,000 threshold\", 6);
        System.out.println(\"ALERT: High value credit transaction detected!\");
end

rule \"High Value Debit Transaction\"
    when
        \$fact : DynamicFact( getPropertyAsNumber(\"debit\").doubleValue() > 50000.0 )
    then
        \$fact.addViolation(\"HIGH_VALUE_DEBIT\", \"Debit transaction exceeds 50,000 threshold\", 6);
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 2: Unusual Transaction Pattern
create_rule \
    "Transaction Unusual Pattern Detection" \
    "transactions" \
    "Detects unusual transaction patterns including negative closing balance and excessive withdrawal" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Negative Closing Balance\"
    when
        \$fact : DynamicFact( getPropertyAsNumber(\"closingBalance\").doubleValue() < 0 )
    then
        \$fact.addViolation(\"NEGATIVE_BALANCE\", \"Account has negative closing balance\", 7);
        System.out.println(\"ALERT: Negative balance detected!\");
end

rule \"Unusual Cash Withdrawal\"
    when
        \$fact : DynamicFact( 
            getPropertyAsString(\"source\").equals(\"CASH WITHDRAWAL\") &&
            getPropertyAsNumber(\"debit\").doubleValue() > 20000
        )
    then
        \$fact.addViolation(\"UNUSUAL_CASH_WITHDRAWAL\", \"Large cash withdrawal detected\", 5);
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 3: Missing Transaction Details
create_rule \
    "Transaction Missing Details" \
    "transactions" \
    "Flags transactions missing critical information" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Missing Transaction Narrative\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"narrative\") || 
            getPropertyAsString(\"narrative\").isEmpty() ||
            getPropertyAsString(\"narrative\").trim().length() < 3
        )
    then
        \$fact.addViolation(\"MISSING_NARRATIVE\", \"Transaction narrative is missing or too short\", 4);
end

rule \"Missing Transaction Source\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"source\") || 
            getPropertyAsString(\"source\").isEmpty()
        )
    then
        \$fact.addViolation(\"MISSING_SOURCE\", \"Transaction source is missing\", 5);
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 4: Anomaly Detection Support
create_rule \
    "Transaction Anomaly Flag Support" \
    "transactions" \
    "Provides additional risk scoring for transactions marked as anomalies" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Marked As Anomaly\"
    when
        \$fact : DynamicFact( getPropertyAsNumber(\"is_anomaly\").intValue() == 1 )
    then
        \$fact.addViolation(\"DETECTED_ANOMALY\", \"Transaction has been flagged by anomaly detection system\", 9);
        System.out.println(\"ALERT: Anomaly detected in transaction!\");
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 5: Suspicious Activity Patterns
create_rule \
    "Transaction Suspicious Activity Patterns" \
    "transactions" \
    "Detects patterns of suspicious activity in transactions" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Same Day Large Transfer\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"credit\").doubleValue() > 100000 &&
            getPropertyAsNumber(\"debit\").doubleValue() == 0
        )
    then
        \$fact.addViolation(\"LARGE_SAME_DAY_TRANSFER\", \"Very large credit transaction on same day\", 5);
end

rule \"Rapid Transaction Fluctuation\"
    when
        \$fact : DynamicFact( 
            Math.abs(getPropertyAsNumber(\"credit\").doubleValue() - getPropertyAsNumber(\"debit\").doubleValue()) > 50000
        )
    then
        \$fact.addViolation(\"RAPID_FLUCTUATION\", \"Rapid account balance fluctuation detected\", 4);
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 6: Cash Transaction Patterns
create_rule \
    "Transaction Cash Transaction Analysis" \
    "transactions" \
    "Analyzes cash deposit and withdrawal patterns for fraud indicators" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Repeated Cash Deposits\"
    when
        \$fact : DynamicFact( 
            getPropertyAsString(\"source\").contains(\"CASH\") &&
            getPropertyAsNumber(\"credit\").doubleValue() > 20000 &&
            getPropertyAsNumber(\"debit\").doubleValue() == 0
        )
    then
        \$fact.addViolation(\"REPEATED_CASH_DEPOSITS\", \"Large repeated cash deposits detected\", 5);
end

rule \"Excessive Cash Withdrawals\"
    when
        \$fact : DynamicFact( 
            getPropertyAsString(\"source\").equals(\"CASH WITHDRAWAL\") &&
            getPropertyAsNumber(\"debit\").doubleValue() > 100000
        )
    then
        \$fact.addViolation(\"EXCESSIVE_CASH_WITHDRAWAL\", \"Very large cash withdrawal detected\", 7);
        System.out.println(\"ALERT: Excessive cash withdrawal detected!\");
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 7: Transaction Consistency Checks
create_rule \
    "Transaction Consistency Validation" \
    "transactions" \
    "Validates transaction consistency and logical correctness" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Inconsistent Balance Calculation\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"credit\").doubleValue() > 0 &&
            getPropertyAsNumber(\"debit\").doubleValue() > 0
        )
    then
        \$fact.addViolation(\"INCONSISTENT_TRANSACTION\", \"Both credit and debit have values simultaneously\", 8);
        System.out.println(\"ALERT: Inconsistent transaction detected!\");
end

rule \"Zero Amount Transaction\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"credit\").doubleValue() == 0 &&
            getPropertyAsNumber(\"debit\").doubleValue() == 0
        )
    then
        \$fact.addViolation(\"ZERO_AMOUNT_TRANSACTION\", \"Transaction has zero amount\", 3);
end

rule \"Excessive Balance\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"closingBalance\").doubleValue() > 10000000
        )
    then
        \$fact.addViolation(\"EXCESSIVE_BALANCE\", \"Closing balance exceeds normal limits\", 5);
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 8: Timestamp and Date Validation
create_rule \
    "Transaction Date and Time Validation" \
    "transactions" \
    "Validates transaction timestamps and detects unusual timing patterns" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Missing Transaction Date\"
    when
        \$fact : DynamicFact( 
            !hasProperty(\"date\") || 
            getPropertyAsString(\"date\").isEmpty()
        )
    then
        \$fact.addViolation(\"MISSING_DATE\", \"Transaction date is missing\", 6);
end

rule \"Future Dated Transaction\"
    when
        \$fact : DynamicFact( 
            hasProperty(\"date\") && 
            getPropertyAsString(\"date\").compareTo(\"2025-01-01\") > 0
        )
    then
        \$fact.addViolation(\"FUTURE_DATE\", \"Transaction date is in the future\", 9);
        System.out.println(\"ALERT: Future dated transaction detected!\");
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 9: Unusual Transaction Types
create_rule \
    "Transaction Type Risk Analysis" \
    "transactions" \
    "Identifies risky transaction types and sources" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Cryptocurrency Transaction\"
    when
        \$fact : DynamicFact( 
            getPropertyAsString(\"narrative\").toLowerCase().contains(\"crypto\") ||
            getPropertyAsString(\"source\").toLowerCase().contains(\"crypto\")
        )
    then
        \$fact.addViolation(\"CRYPTO_TRANSACTION\", \"Cryptocurrency transaction detected - high risk\", 8);
        System.out.println(\"ALERT: Cryptocurrency transaction detected!\");
end

rule \"International Transfer\"
    when
        \$fact : DynamicFact( 
            getPropertyAsString(\"source\").toUpperCase().contains(\"WIRE\") ||
            getPropertyAsString(\"narrative\").toUpperCase().contains(\"INTERNATIONAL\")
        )
    then
        \$fact.addViolation(\"INTERNATIONAL_TRANSFER\", \"International transfer requires review\", 6);
end

rule \"Unusual Transaction Source\"
    when
        \$fact : DynamicFact( 
            getPropertyAsString(\"source\").isEmpty() ||
            getPropertyAsString(\"source\").toLowerCase().equals(\"unknown\")
        )
    then
        \$fact.addViolation(\"UNUSUAL_SOURCE\", \"Transaction source is unknown or unusual\", 5);
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 10: Rapid Transaction Sequence Detection
create_rule \
    "Transaction Rapid Sequence Detection" \
    "transactions" \
    "Detects rapid sequences of transactions that may indicate fraud" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Structured Transaction Pattern\"
    when
        \$fact : DynamicFact( 
            (getPropertyAsNumber(\"credit\").doubleValue() > 9000 && getPropertyAsNumber(\"credit\").doubleValue() < 10000) ||
            (getPropertyAsNumber(\"debit\").doubleValue() > 9000 && getPropertyAsNumber(\"debit\").doubleValue() < 10000)
        )
    then
        \$fact.addViolation(\"STRUCTURED_TRANSACTION\", \"Transaction amount just below threshold - potential structuring\", 7);
        System.out.println(\"ALERT: Potential transaction structuring detected!\");
end" \
    "ACTIVE" \
    "system"

# Transaction Rule 11: Balance Validation
create_rule \
    "Transaction Balance Validation" \
    "transactions" \
    "Validates account balances and transaction amounts for consistency" \
    "package rules;

import com.frauddetection.domain.DynamicFact;

rule \"Insufficient Funds\"
    when
        \$fact : DynamicFact( 
            getPropertyAsNumber(\"debit\").doubleValue() > getPropertyAsNumber(\"closingBalance\").doubleValue() + getPropertyAsNumber(\"debit\").doubleValue()
        )
    then
        \$fact.addViolation(\"INSUFFICIENT_FUNDS\", \"Debit exceeds available balance\", 6);
end

rule \"Suspicious Round Amount\"
    when
        \$fact : DynamicFact( 
            (getPropertyAsNumber(\"credit\").doubleValue() % 10000 == 0 && getPropertyAsNumber(\"credit\").doubleValue() > 50000) ||
            (getPropertyAsNumber(\"debit\").doubleValue() % 10000 == 0 && getPropertyAsNumber(\"debit\").doubleValue() > 50000)
        )
    then
        \$fact.addViolation(\"ROUND_AMOUNT\", \"Suspicious round amount transaction\", 4);
end" \
    "ACTIVE" \
    "system"

echo ""
echo "========================================="
echo "Rules creation completed!"
echo "========================================="
echo ""
echo "Summary:"
echo "- KYC Rules: 9 rule groups created"
echo "- Transaction Rules: 11 rule groups created"
echo ""
echo "You can now use these rules to evaluate KYC and Transaction data"
echo "against fraud patterns and risk indicators."
echo ""
echo "To test the rules, use the evaluation endpoint:"
echo "  POST $RULE_ENGINE_URL/api/evaluate"
echo ""
echo "Example request body:"
echo '  {'
echo '    "dataType": "kyc",'
echo '    "facts": [{'
echo '      "customer_age": 16,'
echo '      "customer_name": "Test User"'
echo '    }]'
echo '  }'
echo ""


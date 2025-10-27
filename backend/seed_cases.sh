#!/bin/bash

# Seed Cases for Analyst Users - Self-contained script
# This script creates dummy flagged items and case assignments for testing
# Usage: ./seed_cases.sh [database_url]

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Fraud Detection System - Seed Cases for Analyst Users ===${NC}\n"

# Get database URL from argument or environment variable
DB_URL="${1:-${DATABASE_URL}}"

if [ -z "$DB_URL" ]; then
    echo -e "${RED}Error: No database URL provided${NC}"
    echo "Usage: $0 <database_url>"
    echo "Example: $0 'postgresql://user:password@localhost:5432/fraud_detection'"
    echo "Or set DATABASE_URL environment variable"
    exit 1
fi

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql command not found. Please install PostgreSQL client.${NC}"
    exit 1
fi

echo -e "${YELLOW}→ Connecting to database...${NC}\n"

# Create dummy flagged items for different data types
psql "$DB_URL" <<'EOF'
-- Create dummy flagged items for different data types
INSERT INTO flagged_items (id, type, data_id, reason, risk_score, status, details, rule_engine_score, ml_score, anomaly_score, flagged_by, created_at, updated_at)
VALUES
    -- High-risk transactions
    ('f1111111-1111-1111-1111-111111111111', 'transactions', 'TXN-2024-001', 'Unusual transaction pattern detected - Multiple large withdrawals', 89.5, 'pending', '{"amount": 15000, "currency": "USD", "location": "Nigeria", "time": "03:45 AM"}', 92.0, 88.0, 89.0, 'system', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    ('f2222222-2222-2222-2222-222222222222', 'transactions', 'TXN-2024-002', 'Suspicious velocity - 10 transactions in 5 minutes', 95.2, 'pending', '{"amount": 500, "currency": "USD", "merchant": "Online Casino", "frequency": "high"}', 96.0, 94.0, 95.5, 'system', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    ('f3333333-3333-3333-3333-333333333333', 'transactions', 'TXN-2024-003', 'Geographic anomaly - Transaction from unusual country', 78.3, 'pending', '{"amount": 8500, "currency": "EUR", "location": "Russia", "previous_location": "USA"}', 75.0, 82.0, 78.0, 'system', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours'),
    

    -- KYC issues
    ('f7777777-7777-7777-7777-777777777777', 'kyc', 'KYC-2024-001', 'Document verification failed - Possible forgery detected', 96.8, 'pending', '{"document_type": "passport", "issue": "inconsistent_font", "ai_confidence": 0.97}', 98.0, 96.0, 96.5, 'system', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours'),
    ('f8888888-8888-8888-8888-888888888888', 'kyc', 'KYC-2024-002', 'Identity theft indicators - Multiple accounts with same SSN', 88.9, 'pending', '{"ssn": "***-**-1234", "matching_accounts": 5, "different_addresses": true}', 90.0, 88.5, 88.2, 'system', NOW() - INTERVAL '8 hours', NOW() - INTERVAL '8 hours'),
    
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully created 15 flagged items${NC}"
else
    echo -e "${RED}✗ Failed to create flagged items${NC}"
    exit 1
fi

# Create case assignments for the existing analyst user
psql "$DB_URL" <<'EOF'
-- Create case assignments for the existing analyst user
INSERT INTO case_assignments (id, flagged_item_id, auditor_id, assigned_by, assigned_at, status, priority, due_date, notes, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    flagged_item_id,
    analyst_id,
    'system',
    assigned_at,
    status,
    priority,
    due_date,
    notes,
    created_at,
    updated_at
FROM (
    SELECT (SELECT id FROM users WHERE role = 'analyst' LIMIT 1) as analyst_id
) analyst
CROSS JOIN (
    VALUES
        ('f1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '2 days', 'in_progress', 'high', NOW() + INTERVAL '1 day', 'High priority case - requires immediate attention', NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 hour'),
        ('f2222222-2222-2222-2222-222222222222', NOW() - INTERVAL '1 day', 'assigned', 'urgent', NOW() + INTERVAL '6 hours', 'Casino transactions - check for gambling addiction patterns', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
        ('f7777777-7777-7777-7777-777777777777', NOW() - INTERVAL '4 hours', 'assigned', 'urgent', NOW() + INTERVAL '4 hours', 'Suspected document forgery - verify with document team', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours'),
        ('fddddddd-dddd-dddd-dddd-dddddddddddd', NOW() - INTERVAL '30 minutes', 'assigned', 'high', NOW() + INTERVAL '2 hours', 'Possible structuring - review transaction history', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
        ('f4444444-4444-4444-4444-444444444444', NOW() - INTERVAL '5 hours', 'in_progress', 'high', NOW() + INTERVAL '12 hours', 'Income mismatch - request additional documentation', NOW() - INTERVAL '5 hours', NOW() - INTERVAL '2 hours'),
        ('f5555555-5555-5555-5555-555555555555', NOW() - INTERVAL '1 day', 'assigned', 'high', NOW() + INTERVAL '8 hours', 'Multiple loan applications - coordinate with credit bureau', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
        ('f8888888-8888-8888-8888-888888888888', NOW() - INTERVAL '8 hours', 'assigned', 'urgent', NOW() + INTERVAL '3 hours', 'Potential identity theft - escalate if confirmed', NOW() - INTERVAL '8 hours', NOW() - INTERVAL '8 hours'),
        ('f9999999-9999-9999-9999-999999999999', NOW() - INTERVAL '12 hours', 'assigned', 'medium', NOW() + INTERVAL '1 day', 'Credit score manipulation suspected', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours'),
        ('feeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', NOW() - INTERVAL '2 hours', 'assigned', 'urgent', NOW() + INTERVAL '2 hours', 'PEP match - enhanced due diligence required', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours'),
        ('f3333333-3333-3333-3333-333333333333', NOW() - INTERVAL '3 hours', 'assigned', 'medium', NOW() + INTERVAL '1 day', 'Geographic anomaly - verify with customer', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours'),
        ('f6666666-6666-6666-6666-666666666666', NOW() - INTERVAL '6 hours', 'assigned', 'medium', NOW() + INTERVAL '2 days', 'High DTI ratio - assess repayment capacity', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours'),
        ('faaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', NOW() - INTERVAL '18 hours', 'assigned', 'low', NOW() + INTERVAL '3 days', 'Negative payment history - standard review', NOW() - INTERVAL '18 hours', NOW() - INTERVAL '18 hours'),
        ('fbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', NOW() - INTERVAL '1 day', 'assigned', 'low', NOW() + INTERVAL '2 days', 'Payment source change - routine verification', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
        ('fcccccc8-cccc-cccc-cccc-cccccccccccc', NOW() - INTERVAL '6 hours', 'assigned', 'low', NOW() + INTERVAL '3 days', 'Minor payment irregularity', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours'),
        ('ffffffff-ffff-ffff-ffff-ffffffffffff', NOW() - INTERVAL '4 hours', 'assigned', 'high', NOW() + INTERVAL '8 hours', 'Synthetic identity suspected - thorough investigation needed', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours')
) AS cases(flagged_item_id, assigned_at, status, priority, due_date, notes, created_at, updated_at);
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully created case assignments${NC}"
else
    echo -e "${RED}✗ Failed to create case assignments${NC}"
    exit 1
fi

# Display summary
echo -e "\n${GREEN}✓ Successfully seeded cases for analyst users!${NC}\n"
echo -e "${YELLOW}Summary:${NC}"
echo "  • 15 flagged items created (transactions, loans, KYC, credit, repayments)"
echo "  • 15 case assignments created for analyst user"
echo "  • Priority levels: urgent, high, medium, low"
echo ""
echo -e "${YELLOW}Test Users:${NC}"
echo "  • analyst1@fraud-detection.com (password: analyst123)"
echo "  • analyst2@fraud-detection.com (password: analyst123)"
echo "  • analyst3@fraud-detection.com (password: analyst123)"
echo ""
echo -e "${GREEN}You can now log in with any analyst account to see their assigned cases.${NC}\n"


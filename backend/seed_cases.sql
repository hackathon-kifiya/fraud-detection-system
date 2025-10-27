-- Seed Cases for Analyst Users
-- This is a disposable script to create dummy flagged items and case assignments

-- Get the existing analyst user ID (we'll use this for all assignments)
-- If you want a specific analyst, check with: SELECT id, email FROM users WHERE role = 'analyst';

-- Create dummy flagged items for different data types
INSERT INTO flagged_items (id, type, data_id, reason, risk_score, status, details, rule_engine_score, ml_score, anomaly_score, flagged_by, created_at, updated_at)
VALUES
    -- High-risk transactions
    ('f1111111-1111-1111-1111-111111111111', 'transactions', 'TXN-2024-001', 'Unusual transaction pattern detected - Multiple large withdrawals', 89.5, 'pending', '{"amount": 15000, "currency": "USD", "location": "Nigeria", "time": "03:45 AM"}', 92.0, 88.0, 89.0, 'system', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    ('f2222222-2222-2222-2222-222222222222', 'transactions', 'TXN-2024-002', 'Suspicious velocity - 10 transactions in 5 minutes', 95.2, 'pending', '{"amount": 500, "currency": "USD", "merchant": "Online Casino", "frequency": "high"}', 96.0, 94.0, 95.5, 'system', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    ('f3333333-3333-3333-3333-333333333333', 'transactions', 'TXN-2024-003', 'Geographic anomaly - Transaction from unusual country', 78.3, 'pending', '{"amount": 8500, "currency": "EUR", "location": "Russia", "previous_location": "USA"}', 75.0, 82.0, 78.0, 'system', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours'),
    
    -- Loan requests
    ('f4444444-4444-4444-4444-444444444444', 'loan_requests', 'LOAN-2024-001', 'Income verification mismatch - Stated income vs documented', 85.7, 'pending', '{"loan_amount": 50000, "stated_income": 120000, "verified_income": 45000, "credit_score": 620}', 88.0, 84.0, 85.0, 'system', NOW() - INTERVAL '5 hours', NOW() - INTERVAL '5 hours'),
    ('f5555555-5555-5555-5555-555555555555', 'loan_requests', 'LOAN-2024-002', 'Multiple recent loan applications across institutions', 92.1, 'pending', '{"loan_amount": 35000, "applications_last_30_days": 8, "credit_score": 580}', 94.0, 91.0, 91.5, 'system', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    ('f6666666-6666-6666-6666-666666666666', 'loan_requests', 'LOAN-2024-003', 'High debt-to-income ratio detected', 73.5, 'pending', '{"loan_amount": 25000, "monthly_income": 3500, "monthly_debt": 2800, "dti_ratio": 0.80}', 70.0, 76.0, 74.5, 'system', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours'),
    
    -- KYC issues
    ('f7777777-7777-7777-7777-777777777777', 'kyc', 'KYC-2024-001', 'Document verification failed - Possible forgery detected', 96.8, 'pending', '{"document_type": "passport", "issue": "inconsistent_font", "ai_confidence": 0.97}', 98.0, 96.0, 96.5, 'system', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours'),
    ('f8888888-8888-8888-8888-888888888888', 'kyc', 'KYC-2024-002', 'Identity theft indicators - Multiple accounts with same SSN', 88.9, 'pending', '{"ssn": "***-**-1234", "matching_accounts": 5, "different_addresses": true}', 90.0, 88.5, 88.2, 'system', NOW() - INTERVAL '8 hours', NOW() - INTERVAL '8 hours'),
    
    -- Credit history
    ('f9999999-9999-9999-9999-999999999999', 'credit_history', 'CREDIT-2024-001', 'Sudden credit score improvement - Possible manipulation', 82.4, 'pending', '{"previous_score": 520, "current_score": 750, "change_period_days": 15}', 85.0, 80.0, 82.0, 'system', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours'),
    ('faaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'credit_history', 'CREDIT-2024-002', 'Negative payment history pattern', 76.2, 'pending', '{"missed_payments_6mo": 4, "accounts_in_collections": 2, "recent_bankruptcy": false}', 78.0, 75.0, 75.8, 'system', NOW() - INTERVAL '18 hours', NOW() - INTERVAL '18 hours'),
    
    -- Repayments
    ('fbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'repayments', 'REPAY-2024-001', 'Payment source mismatch - Different account used', 71.3, 'pending', '{"original_account": "****1234", "payment_account": "****5678", "amount": 5000}', 70.0, 72.0, 71.8, 'system', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    ('fcccccc8-cccc-cccc-cccc-cccccccccccc', 'repayments', 'REPAY-2024-002', 'Irregular payment pattern detected', 68.5, 'pending', '{"expected_amount": 1500, "paid_amount": 1501, "payment_time": "unusual"}', 65.0, 71.0, 69.5, 'system', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours'),
    
    -- Additional high-priority cases
    ('fddddddd-dddd-dddd-dddd-dddddddddddd', 'transactions', 'TXN-2024-004', 'Structuring behavior - Multiple transactions just under reporting threshold', 91.7, 'pending', '{"transactions": [9800, 9750, 9900], "period": "2 hours", "threshold": 10000}', 93.0, 90.5, 91.6, 'system', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
    ('feeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'kyc', 'KYC-2024-003', 'PEP match - Politically Exposed Person identified', 87.4, 'pending', '{"match_confidence": 0.89, "source": "OFAC", "country": "Unknown"}', 90.0, 85.0, 87.2, 'system', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours'),
    ('ffffffff-ffff-ffff-ffff-ffffffffffff', 'loan_requests', 'LOAN-2024-004', 'Synthetic identity suspected', 94.6, 'pending', '{"credit_history_length": "2 months", "credit_mix": "limited", "recent_accounts": 5}', 96.0, 93.5, 94.3, 'system', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours');

-- Create case assignments for the existing analyst user
-- This will assign all cases to the first analyst user found
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

-- Summary of seeded data
SELECT 
    'Seeded Data Summary' as info,
    (SELECT email FROM users WHERE role = 'analyst' LIMIT 1) as analyst_email,
    (SELECT COUNT(*) FROM flagged_items WHERE status = 'pending') as pending_flagged_items,
    (SELECT COUNT(*) FROM case_assignments WHERE auditor_id::text = (SELECT id::text FROM users WHERE role = 'analyst' LIMIT 1)) as total_case_assignments,
    (SELECT COUNT(*) FROM case_assignments WHERE status = 'assigned' AND auditor_id::text = (SELECT id::text FROM users WHERE role = 'analyst' LIMIT 1)) as assigned_cases,
    (SELECT COUNT(*) FROM case_assignments WHERE status = 'in_progress' AND auditor_id::text = (SELECT id::text FROM users WHERE role = 'analyst' LIMIT 1)) as in_progress_cases;

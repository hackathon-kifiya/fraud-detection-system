-- Fraud Detection MVP Database Schema
-- PostgreSQL 15+ with JSONB support

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'frauduser') THEN
        CREATE ROLE frauduser WITH LOGIN PASSWORD 'fraudpass';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE frauddb TO frauduser;

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    txn_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('credit', 'debit')),
    payment_method VARCHAR(50) NOT NULL,
    items JSONB,
    account_balance NUMERIC(15,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Loan requests table
CREATE TABLE IF NOT EXISTS loan_requests (
    loan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL,
    amount_requested NUMERIC(15,2) NOT NULL,
    purpose TEXT,
    request_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Credit history table
CREATE TABLE IF NOT EXISTS credit_history (
    user_id VARCHAR(50) PRIMARY KEY,
    credit_score INTEGER NOT NULL CHECK (credit_score >= 300 AND credit_score <= 850),
    past_loans JSONB,
    defaults_count INTEGER DEFAULT 0 CHECK (defaults_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- KYC table
CREATE TABLE IF NOT EXISTS kyc (
    user_id VARCHAR(50) PRIMARY KEY,
    verified_status BOOLEAN NOT NULL DEFAULT FALSE,
    documents JSONB,
    verification_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Repayments table
CREATE TABLE IF NOT EXISTS repayments (
    repayment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL,
    loan_id UUID NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('paid', 'late', 'default')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Flagged items table
CREATE TABLE IF NOT EXISTS flagged_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(20) NOT NULL CHECK (type IN ('transaction', 'loan', 'repayment', 'user')),
    ref_id UUID NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    score NUMERIC(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    reasons JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'fraud', 'safe')),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

CREATE INDEX IF NOT EXISTS idx_loan_requests_user_id ON loan_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_loan_requests_timestamp ON loan_requests(request_timestamp);

CREATE INDEX IF NOT EXISTS idx_repayments_user_id ON repayments(user_id);
CREATE INDEX IF NOT EXISTS idx_repayments_loan_id ON repayments(loan_id);
CREATE INDEX IF NOT EXISTS idx_repayments_timestamp ON repayments(timestamp);
CREATE INDEX IF NOT EXISTS idx_repayments_status ON repayments(status);

CREATE INDEX IF NOT EXISTS idx_flagged_items_user_id ON flagged_items(user_id);
CREATE INDEX IF NOT EXISTS idx_flagged_items_type ON flagged_items(type);
CREATE INDEX IF NOT EXISTS idx_flagged_items_status ON flagged_items(status);
CREATE INDEX IF NOT EXISTS idx_flagged_items_score ON flagged_items(score);
CREATE INDEX IF NOT EXISTS idx_flagged_items_created_at ON flagged_items(created_at);

-- Create foreign key constraints
ALTER TABLE repayments 
ADD CONSTRAINT fk_repayments_loan_id 
FOREIGN KEY (loan_id) REFERENCES loan_requests(loan_id) ON DELETE CASCADE;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_credit_history_updated_at 
    BEFORE UPDATE ON credit_history 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_kyc_updated_at 
    BEFORE UPDATE ON kyc 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant all privileges on tables to frauduser
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO frauduser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO frauduser;

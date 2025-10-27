-- Database Schema for Rule Engine

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Rule table
CREATE TABLE IF NOT EXISTS "rule" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    "data_type" VARCHAR(50) NOT NULL,
    "drl_content" TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    version INTEGER DEFAULT 1,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "created_by" VARCHAR(100),
    "updated_by" VARCHAR(100)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_rule_data_type ON "rule"("data_type");
CREATE INDEX IF NOT EXISTS idx_rule_status ON "rule"(status);
CREATE INDEX IF NOT EXISTS idx_rule_created_at ON "rule"("created_at");
CREATE INDEX IF NOT EXISTS idx_rule_name ON "rule"(name);

-- Rule version history table (for tracking rule changes)
CREATE TABLE IF NOT EXISTS "rule_version" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID NOT NULL,
    version INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    "data_type" VARCHAR(50) NOT NULL,
    "drl_content" TEXT NOT NULL,
    status VARCHAR(20),
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "created_by" VARCHAR(100),
    CONSTRAINT fk_rule_version_rule FOREIGN KEY (rule_id) REFERENCES "rule"(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rule_version_rule_id ON "rule_version"(rule_id);
CREATE INDEX IF NOT EXISTS idx_rule_version_version ON "rule_version"(version);
CREATE INDEX IF NOT EXISTS idx_rule_version_created_at ON "rule_version"("created_at");


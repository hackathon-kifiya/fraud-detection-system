-- Database Schema for Rule Engine Tests

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Data type table for defining data schemas
CREATE TABLE IF NOT EXISTS "data_type" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "data_type" VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    "schema_definition" JSONB,
    "sample_data" JSONB,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "created_by" VARCHAR(100),
    "updated_by" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_data_type_data_type ON "data_type"("data_type");
CREATE INDEX IF NOT EXISTS idx_data_type_status ON "data_type"(status);
CREATE INDEX IF NOT EXISTS idx_data_type_created_at ON "data_type"("created_at");

-- Rule table
CREATE TABLE IF NOT EXISTS "rule" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    "data_type" VARCHAR(50) NOT NULL,
    "drl_content" TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "created_by" VARCHAR(100),
    "updated_by" VARCHAR(100),
    CONSTRAINT fk_rule_data_type FOREIGN KEY ("data_type") REFERENCES "data_type"("data_type") ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_rule_data_type ON "rule"("data_type");
CREATE INDEX IF NOT EXISTS idx_rule_status ON "rule"(status);
CREATE INDEX IF NOT EXISTS idx_rule_created_at ON "rule"("created_at");


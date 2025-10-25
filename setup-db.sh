#!/bin/bash

# Setup PostgreSQL database for fraud detection system

echo "Setting up PostgreSQL database..."

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "PostgreSQL is not running. Starting PostgreSQL..."
    sudo systemctl start postgresql
    sleep 3
fi

# Create database and user
echo "Creating database and user..."

# Switch to postgres user and create database
sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE fraud_detection;

-- Create user with password
CREATE USER fraud_user WITH PASSWORD 'fraud_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fraud_detection TO fraud_user;

-- Connect to the database and grant schema privileges
\c fraud_detection;
GRANT ALL ON SCHEMA public TO fraud_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fraud_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fraud_user;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\q
EOF

echo "Database setup complete!"
echo "Connection string: postgres://fraud_user:fraud_password@localhost:5432/fraud_detection"

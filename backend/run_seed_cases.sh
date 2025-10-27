#!/bin/bash

# Script to run the seed_cases.sql file
# Usage: ./run_seed_cases.sh [database_url]
# Example: ./run_seed_cases.sh "postgresql://user:password@localhost:5432/fraud_detection"

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

# Check if seed file exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEED_FILE="$SCRIPT_DIR/seed_cases.sql"

if [ ! -f "$SEED_FILE" ]; then
    echo -e "${RED}Error: seed_cases.sql not found at $SEED_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found seed file: $SEED_FILE${NC}"
echo -e "${YELLOW}→ Connecting to database...${NC}\n"

# Run the SQL file
if psql "$DB_URL" -f "$SEED_FILE"; then
    echo -e "\n${GREEN}✓ Successfully seeded cases for analyst users!${NC}\n"
    echo -e "${YELLOW}Test Users Created:${NC}"
    echo "  • analyst1@fraud-detection.com (password: analyst123)"
    echo "  • analyst2@fraud-detection.com (password: analyst123)"
    echo "  • analyst3@fraud-detection.com (password: analyst123)"
    echo ""
    echo -e "${YELLOW}Flagged Items Created:${NC} 15 dummy fraud cases"
    echo -e "${YELLOW}Case Assignments Created:${NC} 16 assignments across 3 analysts"
    echo ""
    echo -e "${GREEN}You can now log in with any analyst account to see their assigned cases.${NC}"
else
    echo -e "\n${RED}✗ Failed to seed database${NC}"
    exit 1
fi


# Rule Engine End-to-End Tests

This directory contains comprehensive integration tests for the Fraud Detection Rule Engine.

## Overview

The end-to-end test (`RuleEngineEndToEndTest.java`) demonstrates the complete workflow:
1. **Creating Rules**: Store business rules in the database
2. **Preparing Data**: Create test data (transactions, loan applications, etc.)
3. **Evaluating**: Run rules against the data
4. **Verifying Results**: Check risk scores and violations

## Test Scenarios

### 1. Transaction Fraud Detection
- **Purpose**: Detect high-risk transactions
- **Rules**: High amount detection, unusual location detection
- **Test Data**: Multiple transactions with varying risk levels
- **Expected**: System identifies high-risk transactions and assigns appropriate risk scores

### 2. Loan Application Risk Assessment
- **Purpose**: Assess loan applications for approval risk
- **Rules**: Credit score checking, debt-to-income ratio evaluation
- **Test Data**: Both risky and good loan applications
- **Expected**: System correctly identifies risky applications

### 3. Rule Validation Testing
- **Purpose**: Ensure invalid rules are rejected
- **Test Data**: Rule with invalid DRL syntax
- **Expected**: ValidationException is thrown

### 4. Rule Management Operations
- **Purpose**: Test CRUD operations on rules
- **Operations**: Create, Retrieve, Activate, Deactivate
- **Expected**: All operations succeed

## Running the Tests

### Prerequisites
- Java 17 or higher
- Maven 3.6+
- Docker (for TestContainers)

### Run All Tests
```bash
mvn test
```

### Run Specific Test Class
```bash
mvn test -Dtest=RuleEngineEndToEndTest
```

### Run Individual Test Method
```bash
mvn test -Dtest=RuleEngineEndToEndTest#testTransactionFraudDetectionWorkflow
```

### Run with Detailed Output
```bash
mvn test -Dtest=RuleEngineEndToEndTest -Dmaven.test.verbose=true
```

## Test Structure

Each test follows this pattern:
1. **Setup**: Create rules in the database
2. **Execute**: Prepare test data and evaluate
3. **Verify**: Assert results and risk scores
4. **Cleanup**: Database is automatically reset between tests

## Key Features

### Human-Readable Output
Tests print clear progress messages:
```
=== STEP 1: Creating Transaction Fraud Detection Rule ===
✓ Rule created successfully with ID: abc-123
=== STEP 2: Preparing Transaction Test Data ===
✓ Prepared 2 transaction facts
=== STEP 3: Evaluating Transactions Against Rules ===
✓ Evaluation completed
```

### Comprehensive Assertions
- Rule creation succeeds
- Test data is prepared correctly
- Evaluation returns valid results
- Risk scores match expected values
- Violations are detected and logged

### Test Containers
Uses TestContainers to spin up a real PostgreSQL database:
- Isolated test environment
- No manual database setup required
- Clean state for each test

## Example Test Output

```
=== STEP 1: Creating Transaction Fraud Detection Rule ===
✓ Rule created successfully with ID: 550e8400-e29b-41d4-a716-446655440000

=== STEP 2: Preparing Transaction Test Data ===
✓ Prepared 2 transaction facts
  - TX-001: High amount transaction ($25,000)
  - TX-002: Transaction from unusual location ($150)

=== STEP 3: Evaluating Transactions Against Rules ===
✓ Evaluation completed
  Risk Score: 12.5
  Violations Count: 2

=== STEP 4: Verifying Results ===
✓ Found 2 violations:
  - HIGH_AMOUNT: Transaction amount exceeds $10,000
  - UNUSUAL_LOCATION: Transaction from unusual location

✓ All assertions passed!
```

## Troubleshooting

### TestContainers Issues
If Docker isn't available, you can use an H2 in-memory database:
```properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
```

### Rule Compilation Errors
If rules fail to compile, check:
1. DRL syntax is correct
2. Package declarations match
3. Imports are properly included

### Database Connection Issues
Ensure Docker is running:
```bash
docker ps
```

## Contributing

When adding new tests:
1. Follow the existing pattern with clear step descriptions
2. Use descriptive test names with `@DisplayName`
3. Print progress messages for readability
4. Include thorough assertions
5. Clean up after the test completes


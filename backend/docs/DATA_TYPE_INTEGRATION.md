# Data Type Management Integration with Rule Engine

## Overview

The backend now automatically syncs all data type operations with the Rule Engine. When you create, update, or delete a data type in the backend, it automatically reflects in the rule engine.

## Architecture

### Components

1. **RuleEngineDataTypeClient** (`backend/internal/adapter/client/ruleengine_datatypes.go`)
   - Handles communication with the rule engine's data type management API
   - Provides methods for creating, updating, deleting, and syncing data types

2. **DataTypeService** (`backend/internal/core/service/data_type_service.go`)
   - Extended with `SetRuleEngineSync()` method to enable syncing
   - Automatically syncs on create, update, and delete operations

3. **Initialization** (`backend/cmd/main.go`)
   - Initializes the rule engine client when rule engine URL is provided
   - Enables syncing in the data type service

## How It Works

### Automatic Syncing

When a data type is:
- **Created**: Automatically synced to rule engine
- **Updated**: Automatically synced to rule engine
- **Deleted**: Automatically deleted from rule engine

### Fallback Behavior

- If rule engine is unavailable, the operation logs a warning but continues
- If the `RULE_ENGINE_URL` environment variable is not set, syncing is disabled

## Configuration

Set the `RULE_ENGINE_URL` environment variable or pass the `-rule_engine_url` flag:

```bash
export RULE_ENGINE_URL=http://rule-engine:8080
./backend -rule_engine_url=http://rule-engine:8080
```

## API Reference

### Rule Engine Data Type API

The rule engine provides the following endpoints (managed by Java backend):

- `POST /api/data-types` - Create a data type
- `GET /api/data-types` - List all data types
- `GET /api/data-types/{id}` - Get data type by ID
- `GET /api/data-types/by-name/{name}` - Get data type by name
- `PUT /api/data-types/{id}` - Update a data type
- `DELETE /api/data-types/{id}` - Delete a data type
- `POST /api/data-types/{id}/activate` - Activate a data type
- `POST /api/data-types/{id}/deactivate` - Deactivate a data type

### Sync Behavior

The `SyncDataType` method:
1. Checks if data type exists in rule engine
2. If it doesn't exist, creates it
3. If it exists, updates it

## Seed Data Integration

When seeding data types on startup:

1. Seed files are loaded from `backend/data/seeds/*-data-type.json`
2. Data types are created in the backend database
3. If rule engine URL is configured, data types are also synced to the rule engine

### Sample Seed Files

- `transactions-data-type.json` - Financial transaction data
- `kyc-data-type.json` - Know Your Customer data

## Error Handling

- Syncing failures are logged as warnings but don't block operations
- Backend operations always succeed, even if rule engine sync fails
- This ensures availability: backend continues to work even if rule engine is down

## Testing

### Verify Syncing

1. Check logs for "Rule engine data type syncing enabled"
2. Create/update/delete a data type via API
3. Verify it appears in the rule engine

### Manual Sync

You can also manually sync data types:

```go
client := client.NewRuleEngineDataTypeClient("http://rule-engine:8080")
client.SyncDataType(dataTypeRequest)
```

## Benefits

1. **Automatic Synchronization**: No manual steps needed
2. **Consistency**: Backend and rule engine always stay in sync
3. **Resilience**: Failures don't affect backend availability
4. **Simplified Management**: One source of truth (backend) manages everything

## Troubleshooting

### Syncing not working?

1. Check if `RULE_ENGINE_URL` is set correctly
2. Verify rule engine is running and accessible
3. Check logs for sync errors
4. Ensure network connectivity between services

### Data type not in rule engine?

1. Check rule engine logs
2. Verify the data type was created in backend
3. Try manually calling the sync endpoint
4. Check for network/authentication issues

## Future Enhancements

- Add retry logic for failed syncs
- Add periodic sync verification
- Add metrics for sync success/failure rates
- Add rollback on sync failure (configurable)


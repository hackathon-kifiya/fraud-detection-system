package client

import (
	"context"
	"encoding/json"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
)

// DataTypeRepositoryAdapter implements DataTypeRepository by delegating to Data Management Service
type DataTypeRepositoryAdapter struct {
	client *DataManagementClient
}

// NewDataTypeRepositoryAdapter creates a new adapter that fetches from Data Management Service
func NewDataTypeRepositoryAdapter(client *DataManagementClient) *DataTypeRepositoryAdapter {
	return &DataTypeRepositoryAdapter{
		client: client,
	}
}

// Convert DataManagementDataTypeResponse to domain.DataType
func (a *DataTypeRepositoryAdapter) convertToDomain(dt *DataManagementDataTypeResponse) *domain.DataType {
	// Marshal schema and sample data back to JSON strings
	schemaBytes, _ := json.Marshal(dt.SchemaDefinition)
	sampleBytes, _ := json.Marshal(dt.SampleData)

	return &domain.DataType{
		ID:               dt.DataType,
		DataType:         dt.DataType,
		Name:             dt.Name,
		Description:      dt.Description,
		SchemaDefinition: string(schemaBytes),
		SampleData:       string(sampleBytes),
		Status:           dt.Status,
		CreatedBy:        dt.CreatedBy,
		UpdatedBy:        dt.UpdatedBy,
	}
}

// Note: These operations are read-only since we're fetching from Data Management Service
// Write operations will fail with appropriate errors

func (a *DataTypeRepositoryAdapter) Create(ctx context.Context, dataType *domain.DataType) error {
	return fmt.Errorf("data types must be managed through the Data Management Service")
}

func (a *DataTypeRepositoryAdapter) GetByID(ctx context.Context, id string) (*domain.DataType, error) {
	return a.GetByDataType(ctx, id)
}

func (a *DataTypeRepositoryAdapter) GetByDataType(ctx context.Context, dataType string) (*domain.DataType, error) {
	response, err := a.client.GetDataType(dataType)
	if err != nil {
		return nil, err
	}
	return a.convertToDomain(response), nil
}

func (a *DataTypeRepositoryAdapter) Exists(ctx context.Context, dataType string) (bool, error) {
	_, err := a.client.GetDataType(dataType)
	if err != nil {
		// If it's a not found error, return false
		if err.Error() == fmt.Sprintf("data type '%s' not found", dataType) {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

func (a *DataTypeRepositoryAdapter) Update(ctx context.Context, dataType *domain.DataType) error {
	return fmt.Errorf("data types must be managed through the Data Management Service")
}

func (a *DataTypeRepositoryAdapter) Delete(ctx context.Context, id string) error {
	return fmt.Errorf("data types must be managed through the Data Management Service")
}

func (a *DataTypeRepositoryAdapter) List(ctx context.Context, limit, offset int) ([]domain.DataType, int64, error) {
	responses, err := a.client.GetAllDataTypes()
	if err != nil {
		return nil, 0, err
	}

	result := make([]domain.DataType, len(responses))
	for i, response := range responses {
		result[i] = *a.convertToDomain(&response)
	}

	return result, int64(len(result)), nil
}

func (a *DataTypeRepositoryAdapter) Count(ctx context.Context) (int64, error) {
	responses, err := a.client.GetAllDataTypes()
	if err != nil {
		return 0, err
	}
	return int64(len(responses)), nil
}

func (a *DataTypeRepositoryAdapter) GetByStatus(ctx context.Context, status string) ([]domain.DataType, error) {
	responses, err := a.client.GetAllDataTypes()
	if err != nil {
		return nil, err
	}

	var result []domain.DataType
	for _, response := range responses {
		if response.Status == status {
			result = append(result, *a.convertToDomain(&response))
		}
	}

	return result, nil
}

func (a *DataTypeRepositoryAdapter) GetActive(ctx context.Context) ([]domain.DataType, error) {
	return a.GetByStatus(ctx, "ACTIVE")
}

func (a *DataTypeRepositoryAdapter) Search(ctx context.Context, query string) ([]domain.DataType, error) {
	// Simple implementation - fetch all and filter
	all, _, err := a.List(ctx, 0, 0)
	if err != nil {
		return nil, err
	}

	var result []domain.DataType
	for _, dt := range all {
		if contains(query, dt.Name) || contains(query, dt.Description) || contains(query, dt.DataType) {
			result = append(result, dt)
		}
	}

	return result, nil
}

func (a *DataTypeRepositoryAdapter) ExistsByDataTypeAndIDNot(ctx context.Context, dataType string, id string) (bool, error) {
	// Since we're read-only, this is the same as Exists
	return a.Exists(ctx, dataType)
}

func contains(str, substr string) bool {
	return len(str) >= len(substr) && (str == substr || len(substr) == 0)
}

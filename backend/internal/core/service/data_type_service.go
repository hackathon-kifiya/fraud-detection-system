package service

import (
	"context"
	"errors"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

var (
	ErrDataTypeNotFound  = errors.New("data type not found")
	ErrReadOnlyMode      = errors.New("data type modifications must be done through the Data Management Service")
	ErrDuplicateDataType = errors.New("data type already exists")
	ErrInvalidSchema     = errors.New("invalid schema definition")
	ErrDataTypeInUse     = errors.New("data type is in use and cannot be deleted")
)

// DataTypeService handles data type operations by delegating to the Data Management Service via repository adapter
type DataTypeService struct {
	repo port.DataTypeRepository
}

// NewDataTypeService creates a new data type service (read-only, fetches from Data Management Service)
func NewDataTypeService(repo port.DataTypeRepository) *DataTypeService {
	return &DataTypeService{
		repo: repo,
	}
}

// CreateDataType is disabled - data types must be created through Data Management Service
func (s *DataTypeService) CreateDataType(ctx context.Context, req domain.CreateDataTypeRequest) (*domain.DataType, error) {
	return nil, ErrReadOnlyMode
}

// GetDataType retrieves a data type by ID
func (s *DataTypeService) GetDataType(ctx context.Context, id string) (*domain.DataType, error) {
	dataType, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, ErrDataTypeNotFound
	}
	return dataType, nil
}

// GetDataTypeByName retrieves a data type by name
func (s *DataTypeService) GetDataTypeByName(ctx context.Context, dataType string) (*domain.DataType, error) {
	dt, err := s.repo.GetByDataType(ctx, dataType)
	if err != nil {
		return nil, ErrDataTypeNotFound
	}
	return dt, nil
}

// ListDataTypes lists all data types with pagination
func (s *DataTypeService) ListDataTypes(ctx context.Context, limit, offset int) (*domain.DataTypeListResponse, error) {
	dataTypes, total, err := s.repo.List(ctx, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list data types: %w", err)
	}

	return &domain.DataTypeListResponse{
		DataTypes: dataTypes,
		Total:     total,
		Limit:     limit,
		Offset:    offset,
	}, nil
}

// UpdateDataType is disabled - data types must be updated through Data Management Service
func (s *DataTypeService) UpdateDataType(ctx context.Context, id string, req domain.UpdateDataTypeRequest) (*domain.DataType, error) {
	return nil, ErrReadOnlyMode
}

// DeleteDataType is disabled - data types cannot be deleted
func (s *DataTypeService) DeleteDataType(ctx context.Context, id string) error {
	return ErrReadOnlyMode
}

// GetActiveDataTypes retrieves all active data types
func (s *DataTypeService) GetActiveDataTypes(ctx context.Context) ([]domain.DataType, error) {
	dataTypes, err := s.repo.GetActive(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get active data types: %w", err)
	}
	return dataTypes, nil
}

// SearchDataTypes searches data types by query
func (s *DataTypeService) SearchDataTypes(ctx context.Context, query string) ([]domain.DataType, error) {
	dataTypes, err := s.repo.Search(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("failed to search data types: %w", err)
	}
	return dataTypes, nil
}

// The following sync methods are no longer needed - kept for backward compatibility
func (s *DataTypeService) SetRuleEngineSync(client interface{})            {}
func (s *DataTypeService) SetDecisionServiceSync(client interface{})       {}
func (s *DataTypeService) SetDataManagementServiceSync(client interface{}) {}

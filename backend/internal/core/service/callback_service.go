package service

import (
	"context"
	"errors"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/client"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

type CallbackService struct {
	callbackRepo         port.CallbackRepository
	dataManagementClient *client.DataManagementClient
}

func NewCallbackService(callbackRepo port.CallbackRepository, dataManagementClient *client.DataManagementClient) *CallbackService {
	return &CallbackService{
		callbackRepo:         callbackRepo,
		dataManagementClient: dataManagementClient,
	}
}

var (
	ErrCallbackNotFound = errors.New("callback not found")
	ErrInvalidDataType  = errors.New("invalid data type")
)

// CreateCallback creates a new callback
func (s *CallbackService) CreateCallback(ctx context.Context, req domain.CreateCallbackRequest) (*domain.Callback, error) {
	// Validate data type exists in data management service
	if err := s.validateDataType(req.DataType); err != nil {
		return nil, err
	}

	callback := &domain.Callback{
		DataType:    req.DataType,
		CallbackURL: req.CallbackURL,
		Method:      req.Method,
		Headers:     req.Headers,
		IsActive:    req.IsActive,
	}

	err := s.callbackRepo.Create(ctx, callback)
	if err != nil {
		return nil, fmt.Errorf("failed to create callback: %w", err)
	}

	return callback, nil
}

// GetCallback retrieves a callback by ID
func (s *CallbackService) GetCallback(ctx context.Context, id string) (*domain.Callback, error) {
	callback, err := s.callbackRepo.GetByID(ctx, id)
	if err != nil {
		if err.Error() == "callback not found" {
			return nil, ErrCallbackNotFound
		}
		return nil, fmt.Errorf("failed to get callback: %w", err)
	}
	return callback, nil
}

// ListCallbacks lists all callbacks with pagination
func (s *CallbackService) ListCallbacks(ctx context.Context, limit, offset int) ([]domain.Callback, int64, error) {
	callbacks, total, err := s.callbackRepo.List(ctx, limit, offset)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to list callbacks: %w", err)
	}
	return callbacks, total, nil
}

// UpdateCallback updates a callback
func (s *CallbackService) UpdateCallback(ctx context.Context, id string, req domain.UpdateCallbackRequest) (*domain.Callback, error) {
	callback, err := s.callbackRepo.GetByID(ctx, id)
	if err != nil {
		if err.Error() == "callback not found" {
			return nil, ErrCallbackNotFound
		}
		return nil, fmt.Errorf("failed to get callback: %w", err)
	}

	// Update fields if provided
	if req.DataType != nil {
		// Validate data type exists in data management service
		if err := s.validateDataType(*req.DataType); err != nil {
			return nil, err
		}
		callback.DataType = *req.DataType
	}
	if req.CallbackURL != nil {
		callback.CallbackURL = *req.CallbackURL
	}
	if req.Method != nil {
		callback.Method = *req.Method
	}
	if req.Headers != nil {
		callback.Headers = *req.Headers
	}
	if req.IsActive != nil {
		callback.IsActive = *req.IsActive
	}

	err = s.callbackRepo.Update(ctx, callback)
	if err != nil {
		return nil, fmt.Errorf("failed to update callback: %w", err)
	}

	return callback, nil
}

// DeleteCallback deletes a callback
func (s *CallbackService) DeleteCallback(ctx context.Context, id string) error {
	_, err := s.callbackRepo.GetByID(ctx, id)
	if err != nil {
		if err.Error() == "callback not found" {
			return ErrCallbackNotFound
		}
		return fmt.Errorf("failed to get callback: %w", err)
	}

	err = s.callbackRepo.Delete(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to delete callback: %w", err)
	}

	return nil
}

// GetActiveCallbacks retrieves all active callbacks
func (s *CallbackService) GetActiveCallbacks(ctx context.Context) ([]domain.Callback, error) {
	callbacks, err := s.callbackRepo.GetActiveCallbacks(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get active callbacks: %w", err)
	}
	return callbacks, nil
}

// GetCallbacksByDataType retrieves callbacks for a specific data type
func (s *CallbackService) GetCallbacksByDataType(ctx context.Context, dataType string) ([]domain.Callback, error) {
	callbacks, err := s.callbackRepo.GetByDataType(ctx, dataType)
	if err != nil {
		return nil, fmt.Errorf("failed to get callbacks by data type: %w", err)
	}
	return callbacks, nil
}

// validateDataType validates that a data type exists in the data management service
func (s *CallbackService) validateDataType(dataType string) error {
	_, err := s.dataManagementClient.GetDataType(dataType)
	if err != nil {
		return fmt.Errorf("%w: %s does not exist in data management service", ErrInvalidDataType, dataType)
	}
	return nil
}

// GetAvailableDataTypes fetches all available data types from data management service
func (s *CallbackService) GetAvailableDataTypes() ([]client.DataManagementDataTypeResponse, error) {
	dataTypes, err := s.dataManagementClient.GetAllDataTypes()
	if err != nil {
		return nil, fmt.Errorf("failed to fetch data types: %w", err)
	}
	return dataTypes, nil
}

// InvokeCallbacksForEvaluation invokes callbacks with evaluation results asynchronously
func (s *CallbackService) InvokeCallbacksForEvaluation(ctx context.Context, dataType string, payload interface{}) error {
	return s.callbackRepo.SendCallback(ctx, dataType, payload)
}

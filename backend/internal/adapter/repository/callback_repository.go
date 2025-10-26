package repository

import (
	"context"
	"fmt"
	"strings"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"gorm.io/gorm"
)

type CallbackRepository struct {
	db *gorm.DB
}

func NewCallbackRepository(db *gorm.DB) *CallbackRepository {
	return &CallbackRepository{db: db}
}

// Create creates a new callback
func (r *CallbackRepository) Create(ctx context.Context, callback *domain.Callback) error {
	result := r.db.WithContext(ctx).Create(callback)
	if result.Error != nil {
		return fmt.Errorf("failed to create callback: %w", result.Error)
	}
	return nil
}

// GetByID retrieves a callback by ID
func (r *CallbackRepository) GetByID(ctx context.Context, id string) (*domain.Callback, error) {
	var callback domain.Callback
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&callback)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("callback not found")
		}
		return nil, fmt.Errorf("failed to get callback: %w", result.Error)
	}
	return &callback, nil
}

// GetByDataType retrieves callbacks by data type
func (r *CallbackRepository) GetByDataType(ctx context.Context, dataType string) ([]domain.Callback, error) {
	var callbacks []domain.Callback
	result := r.db.WithContext(ctx).Where("data_type = ?", dataType).Find(&callbacks)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to get callbacks by data type: %w", result.Error)
	}
	return callbacks, nil
}

// List retrieves all callbacks with pagination
func (r *CallbackRepository) List(ctx context.Context, limit, offset int) ([]domain.Callback, int64, error) {
	var callbacks []domain.Callback
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.Callback{})

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count callbacks: %w", err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&callbacks)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list callbacks: %w", result.Error)
	}

	return callbacks, total, nil
}

// Update updates a callback
func (r *CallbackRepository) Update(ctx context.Context, callback *domain.Callback) error {
	result := r.db.WithContext(ctx).Save(callback)
	if result.Error != nil {
		return fmt.Errorf("failed to update callback: %w", result.Error)
	}
	return nil
}

// Delete deletes a callback
func (r *CallbackRepository) Delete(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Delete(&domain.Callback{}, "id = ?", id)
	if result.Error != nil {
		return fmt.Errorf("failed to delete callback: %w", result.Error)
	}
	return nil
}

// GetActiveCallbacks retrieves all active callbacks
func (r *CallbackRepository) GetActiveCallbacks(ctx context.Context) ([]domain.Callback, error) {
	var callbacks []domain.Callback
	result := r.db.WithContext(ctx).Where("is_active = ?", true).Find(&callbacks)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to get active callbacks: %w", result.Error)
	}
	return callbacks, nil
}

// SendCallback sends a callback to the configured URL
func (r *CallbackRepository) SendCallback(ctx context.Context, dataType string, payload interface{}) error {
	// Get active callbacks for this data type
	callbacks, err := r.GetByDataType(ctx, dataType)
	if err != nil {
		return fmt.Errorf("failed to get callbacks: %w", err)
	}

	// Filter for active callbacks
	var activeCallbacks []domain.Callback
	for _, cb := range callbacks {
		if cb.IsActive {
			activeCallbacks = append(activeCallbacks, cb)
		}
	}

	// TODO: Implement actual HTTP callback sending logic
	// This would typically use an HTTP client to POST/PUT/PATCH to the callback URL
	// For now, we'll just log that we would send the callback
	
	// Example implementation would be:
	// for _, callback := range activeCallbacks {
	//     client := &http.Client{}
	//     req, _ := http.NewRequest(callback.Method, callback.CallbackURL, payload)
	//     // Parse and set headers
	//     client.Do(req)
	// }

	return nil
}

// Helper function to parse headers string into map
func parseHeaders(headersStr string) (map[string]string, error) {
	headers := make(map[string]string)
	if headersStr == "" {
		return headers, nil
	}
	
	// Simple parsing - in production, use proper JSON parsing
	// This assumes headers are in format: "key1:value1,key2:value2"
	parts := strings.Split(headersStr, ",")
	for _, part := range parts {
		kv := strings.Split(part, ":")
		if len(kv) == 2 {
			headers[strings.TrimSpace(kv[0])] = strings.TrimSpace(kv[1])
		}
	}
	return headers, nil
}


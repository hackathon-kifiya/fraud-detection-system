package port

import (
	"context"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
)

// CallbackRepository defines the interface for callback repository operations
type CallbackRepository interface {
	// Create creates a new callback
	Create(ctx context.Context, callback *domain.Callback) error

	// GetByID retrieves a callback by ID
	GetByID(ctx context.Context, id string) (*domain.Callback, error)

	// GetByDataType retrieves callbacks by data type
	GetByDataType(ctx context.Context, dataType string) ([]domain.Callback, error)

	// List retrieves all callbacks with pagination
	List(ctx context.Context, limit, offset int) ([]domain.Callback, int64, error)

	// Update updates a callback
	Update(ctx context.Context, callback *domain.Callback) error

	// Delete deletes a callback
	Delete(ctx context.Context, id string) error

	// GetActiveCallbacks retrieves all active callbacks
	GetActiveCallbacks(ctx context.Context) ([]domain.Callback, error)
}


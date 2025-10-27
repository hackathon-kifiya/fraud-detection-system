package port

import (
	"context"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
)

// LabeledDataRepository defines the interface for labeled data repository operations
type LabeledDataRepository interface {
	// Create creates a new labeled data entry
	Create(ctx context.Context, labeledData *domain.LabeledData) error

	// GetByID retrieves a labeled data entry by ID
	GetByID(ctx context.Context, id string) (*domain.LabeledData, error)

	// GetByDataType retrieves labeled data entries by data type
	GetByDataType(ctx context.Context, dataType string, limit, offset int) ([]domain.LabeledData, int64, error)

	// List retrieves all labeled data entries with pagination
	List(ctx context.Context, limit, offset int) ([]domain.LabeledData, int64, error)

	// Update updates a labeled data entry
	Update(ctx context.Context, labeledData *domain.LabeledData) error

	// Delete deletes a labeled data entry
	Delete(ctx context.Context, id string) error
}

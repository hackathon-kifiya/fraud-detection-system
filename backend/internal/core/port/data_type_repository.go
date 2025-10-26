package port

import (
	"context"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
)

// DataTypeRepository defines the interface for data type repository operations
type DataTypeRepository interface {
	// Create creates a new data type
	Create(ctx context.Context, dataType *domain.DataType) error

	// GetByID retrieves a data type by ID
	GetByID(ctx context.Context, id string) (*domain.DataType, error)

	// GetByDataType retrieves a data type by data type name
	GetByDataType(ctx context.Context, dataType string) (*domain.DataType, error)

	// Exists checks if a data type exists
	Exists(ctx context.Context, dataType string) (bool, error)

	// Update updates a data type
	Update(ctx context.Context, dataType *domain.DataType) error

	// Delete deletes a data type
	Delete(ctx context.Context, id string) error

	// List retrieves all data types with pagination
	List(ctx context.Context, limit, offset int) ([]domain.DataType, int64, error)

	// Count returns the total number of data types
	Count(ctx context.Context) (int64, error)

	// GetByStatus retrieves data types by status
	GetByStatus(ctx context.Context, status string) ([]domain.DataType, error)

	// GetActive retrieves all active data types
	GetActive(ctx context.Context) ([]domain.DataType, error)

	// Search searches data types by name, data_type, or description
	Search(ctx context.Context, query string) ([]domain.DataType, error)

	// ExistsByDataTypeAndIDNot checks if a data type exists with a different ID
	ExistsByDataTypeAndIDNot(ctx context.Context, dataType string, id string) (bool, error)
}

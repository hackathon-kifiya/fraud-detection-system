package port

import (
	"context"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
)

// FlaggedItemRepository defines the interface for flagged item repository operations
type FlaggedItemRepository interface {
	// Create creates a new flagged item
	Create(ctx context.Context, item *domain.FlaggedItem) error

	// GetByID retrieves a flagged item by ID
	GetByID(ctx context.Context, id string) (*domain.FlaggedItem, error)

	// List retrieves flagged items with pagination and filters
	List(ctx context.Context, limit, offset int, itemType, status string) ([]domain.FlaggedItem, int64, error)

	// Update updates a flagged item
	Update(ctx context.Context, item *domain.FlaggedItem) error

	// Delete deletes a flagged item
	Delete(ctx context.Context, id string) error

	// GetStats retrieves statistics about flagged items
	GetStats(ctx context.Context) (*domain.FlaggedItemStats, error)

	// GetByType retrieves flagged items by type
	GetByType(ctx context.Context, itemType string, limit, offset int) ([]domain.FlaggedItem, int64, error)

	// UpdateStatus updates the status of a flagged item
	UpdateStatus(ctx context.Context, id, status, reviewedBy string) error

	// GetWithOriginalData retrieves a flagged item with original data based on type
	GetWithOriginalData(ctx context.Context, id, itemType string) (*domain.FlaggedItem, interface{}, error)

	// GetByReviewedBy retrieves flagged items reviewed by a specific user
	GetByReviewedBy(ctx context.Context, userID string, limit, offset int) ([]domain.FlaggedItem, int64, error)

	// UpdateClassification updates a flagged item with classification and notes
	UpdateClassification(ctx context.Context, id, status, reviewedBy, notes string) error
}


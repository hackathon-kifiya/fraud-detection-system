package port

import (
	"context"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
)

// AuditNoteRepository defines the interface for audit note repository operations
type AuditNoteRepository interface {
	// Create creates a new audit note
	Create(ctx context.Context, note *domain.AuditNote) error

	// GetByID retrieves an audit note by ID
	GetByID(ctx context.Context, id string) (*domain.AuditNote, error)

	// GetByFlaggedItemID retrieves all audit notes for a flagged item
	GetByFlaggedItemID(ctx context.Context, flaggedItemID string) ([]domain.AuditNote, error)

	// GetByUserID retrieves all audit notes by a specific user
	GetByUserID(ctx context.Context, userID string, limit, offset int) ([]domain.AuditNote, int64, error)

	// List retrieves audit notes with pagination and filters
	List(ctx context.Context, limit, offset int, flaggedItemID, userID string) ([]domain.AuditNote, int64, error)

	// Update updates an audit note
	Update(ctx context.Context, note *domain.AuditNote) error

	// Delete deletes an audit note
	Delete(ctx context.Context, id string) error
}

// AuditLogRepository defines the interface for audit log repository operations
type AuditLogRepository interface {
	// Create creates a new audit log entry
	Create(ctx context.Context, log *domain.AuditLog) error

	// GetByID retrieves an audit log entry by ID
	GetByID(ctx context.Context, id string) (*domain.AuditLog, error)

	// GetByFlaggedItemID retrieves all audit log entries for a flagged item
	GetByFlaggedItemID(ctx context.Context, flaggedItemID string) ([]domain.AuditLog, error)

	// GetByUserID retrieves all audit log entries by a specific user
	GetByUserID(ctx context.Context, userID string, limit, offset int) ([]domain.AuditLog, int64, error)

	// List retrieves audit log entries with pagination and filters
	List(ctx context.Context, limit, offset int, flaggedItemID, userID, action string) ([]domain.AuditLog, int64, error)

	// GetStats retrieves audit statistics for a user
	GetStats(ctx context.Context, userID string) (*domain.AuditStats, error)
}

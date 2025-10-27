package repository

import (
	"context"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

type AuditNoteRepository struct {
	db *gorm.DB
}

// NewAuditNoteRepository creates a new audit note repository
func NewAuditNoteRepository(db *gorm.DB) port.AuditNoteRepository {
	return &AuditNoteRepository{db: db}
}

// Create creates a new audit note
func (r *AuditNoteRepository) Create(ctx context.Context, note *domain.AuditNote) error {
	result := r.db.WithContext(ctx).Create(note)
	if result.Error != nil {
		return fmt.Errorf("failed to create audit note: %w", result.Error)
	}
	return nil
}

// GetByID retrieves an audit note by ID
func (r *AuditNoteRepository) GetByID(ctx context.Context, id string) (*domain.AuditNote, error) {
	var note domain.AuditNote
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&note)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("audit note not found")
		}
		return nil, fmt.Errorf("failed to get audit note: %w", result.Error)
	}
	return &note, nil
}

// GetByFlaggedItemID retrieves all audit notes for a flagged item
func (r *AuditNoteRepository) GetByFlaggedItemID(ctx context.Context, flaggedItemID string) ([]domain.AuditNote, error) {
	var notes []domain.AuditNote
	result := r.db.WithContext(ctx).Where("flagged_item_id = ?", flaggedItemID).Order("created_at ASC").Find(&notes)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to get audit notes by flagged item ID: %w", result.Error)
	}
	return notes, nil
}

// GetByUserID retrieves all audit notes by a specific user
func (r *AuditNoteRepository) GetByUserID(ctx context.Context, userID string, limit, offset int) ([]domain.AuditNote, int64, error) {
	var notes []domain.AuditNote
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.AuditNote{}).Where("user_id = ?", userID)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count audit notes by user ID: %w", err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&notes)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list audit notes by user ID: %w", result.Error)
	}

	return notes, total, nil
}

// List retrieves audit notes with pagination and filters
func (r *AuditNoteRepository) List(ctx context.Context, limit, offset int, flaggedItemID, userID string) ([]domain.AuditNote, int64, error) {
	var notes []domain.AuditNote
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.AuditNote{})

	// Apply filters
	if flaggedItemID != "" {
		query = query.Where("flagged_item_id = ?", flaggedItemID)
	}
	if userID != "" {
		query = query.Where("user_id = ?", userID)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count audit notes: %w", err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&notes)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list audit notes: %w", result.Error)
	}

	return notes, total, nil
}

// Update updates an audit note
func (r *AuditNoteRepository) Update(ctx context.Context, note *domain.AuditNote) error {
	result := r.db.WithContext(ctx).Save(note)
	if result.Error != nil {
		return fmt.Errorf("failed to update audit note: %w", result.Error)
	}
	return nil
}

// Delete deletes an audit note
func (r *AuditNoteRepository) Delete(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Delete(&domain.AuditNote{}, "id = ?", id)
	if result.Error != nil {
		return fmt.Errorf("failed to delete audit note: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("audit note not found")
	}
	return nil
}

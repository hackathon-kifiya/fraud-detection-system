package repository

import (
	"context"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"gorm.io/gorm"
)

// LabeledDataRepository implements the labeled data repository interface
type LabeledDataRepository struct {
	db *gorm.DB
}

// NewLabeledDataRepository creates a new labeled data repository
func NewLabeledDataRepository(db *gorm.DB) *LabeledDataRepository {
	return &LabeledDataRepository{db: db}
}

// Create creates a new labeled data entry
func (r *LabeledDataRepository) Create(ctx context.Context, labeledData *domain.LabeledData) error {
	result := r.db.WithContext(ctx).Create(labeledData)
	if result.Error != nil {
		return fmt.Errorf("failed to create labeled data: %w", result.Error)
	}
	return nil
}

// GetByID retrieves a labeled data entry by ID
func (r *LabeledDataRepository) GetByID(ctx context.Context, id string) (*domain.LabeledData, error) {
	var labeledData domain.LabeledData
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&labeledData)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("labeled data not found")
		}
		return nil, fmt.Errorf("failed to get labeled data: %w", result.Error)
	}
	return &labeledData, nil
}

// GetByDataType retrieves labeled data entries by data type
func (r *LabeledDataRepository) GetByDataType(ctx context.Context, dataType string, limit, offset int) ([]domain.LabeledData, int64, error) {
	var labeledDataList []domain.LabeledData
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.LabeledData{}).Where("data_type = ?", dataType)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count labeled data: %w", err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&labeledDataList)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list labeled data: %w", result.Error)
	}

	return labeledDataList, total, nil
}

// List retrieves all labeled data entries with pagination
func (r *LabeledDataRepository) List(ctx context.Context, limit, offset int) ([]domain.LabeledData, int64, error) {
	var labeledDataList []domain.LabeledData
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.LabeledData{})

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count labeled data: %w", err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&labeledDataList)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list labeled data: %w", result.Error)
	}

	return labeledDataList, total, nil
}

// Update updates a labeled data entry
func (r *LabeledDataRepository) Update(ctx context.Context, labeledData *domain.LabeledData) error {
	result := r.db.WithContext(ctx).Save(labeledData)
	if result.Error != nil {
		return fmt.Errorf("failed to update labeled data: %w", result.Error)
	}
	return nil
}

// Delete deletes a labeled data entry
func (r *LabeledDataRepository) Delete(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Delete(&domain.LabeledData{}, "id = ?", id)
	if result.Error != nil {
		return fmt.Errorf("failed to delete labeled data: %w", result.Error)
	}
	return nil
}

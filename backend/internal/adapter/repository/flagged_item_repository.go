package repository

import (
	"context"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

type FlaggedItemRepository struct {
	db *gorm.DB
}

// NewFlaggedItemRepository creates a new flagged item repository
func NewFlaggedItemRepository(db *gorm.DB) port.FlaggedItemRepository {
	return &FlaggedItemRepository{db: db}
}

// Create creates a new flagged item
func (r *FlaggedItemRepository) Create(ctx context.Context, item *domain.FlaggedItem) error {
	result := r.db.WithContext(ctx).Create(item)
	if result.Error != nil {
		return fmt.Errorf("failed to create flagged item: %w", result.Error)
	}
	return nil
}

// GetByID retrieves a flagged item by ID
func (r *FlaggedItemRepository) GetByID(ctx context.Context, id string) (*domain.FlaggedItem, error) {
	var item domain.FlaggedItem
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&item)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("flagged item not found")
		}
		return nil, fmt.Errorf("failed to get flagged item: %w", result.Error)
	}
	return &item, nil
}

// List retrieves flagged items with pagination and filters
func (r *FlaggedItemRepository) List(ctx context.Context, limit, offset int, itemType, status string) ([]domain.FlaggedItem, int64, error) {
	var items []domain.FlaggedItem
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.FlaggedItem{})

	// Apply filters
	if itemType != "" {
		query = query.Where("type = ?", itemType)
	}
	if status != "" {
		query = query.Where("status = ?", status)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count flagged items: %w", err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&items)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list flagged items: %w", result.Error)
	}

	return items, total, nil
}

// Update updates a flagged item
func (r *FlaggedItemRepository) Update(ctx context.Context, item *domain.FlaggedItem) error {
	result := r.db.WithContext(ctx).Save(item)
	if result.Error != nil {
		return fmt.Errorf("failed to update flagged item: %w", result.Error)
	}
	return nil
}

// Delete deletes a flagged item
func (r *FlaggedItemRepository) Delete(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Delete(&domain.FlaggedItem{}, "id = ?", id)
	if result.Error != nil {
		return fmt.Errorf("failed to delete flagged item: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("flagged item not found")
	}
	return nil
}

// GetStats retrieves statistics about flagged items
func (r *FlaggedItemRepository) GetStats(ctx context.Context) (*domain.FlaggedItemStats, error) {
	var stats domain.FlaggedItemStats

	// Get total flagged count
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Count(&stats.TotalFlagged).Error; err != nil {
		return nil, fmt.Errorf("failed to get total flagged count: %w", err)
	}

	// Get pending review count
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("status = ?", domain.StatusPending).Count(&stats.PendingReview).Error; err != nil {
		return nil, fmt.Errorf("failed to get pending review count: %w", err)
	}

	// Get confirmed fraud count
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("status = ?", domain.StatusConfirmed).Count(&stats.ConfirmedFraud).Error; err != nil {
		return nil, fmt.Errorf("failed to get confirmed fraud count: %w", err)
	}

	// Get false positives count
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("status = ?", domain.StatusFalsePositive).Count(&stats.FalsePositives).Error; err != nil {
		return nil, fmt.Errorf("failed to get false positives count: %w", err)
	}

	// Get high risk count (risk score > 80)
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("risk_score > ?", 80).Count(&stats.HighRiskCount).Error; err != nil {
		return nil, fmt.Errorf("failed to get high risk count: %w", err)
	}

	// Get flagged by type
	stats.FlaggedByType = make(map[string]int64)
	types := []string{domain.TypeTransactions, domain.TypeLoanRequests, domain.TypeCreditHistory, domain.TypeKYC, domain.TypeRepayments}

	for _, itemType := range types {
		var count int64
		if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("type = ?", itemType).Count(&count).Error; err != nil {
			return nil, fmt.Errorf("failed to get count for type %s: %w", itemType, err)
		}
		stats.FlaggedByType[itemType] = count
	}

	return &stats, nil
}

// GetByType retrieves flagged items by type
func (r *FlaggedItemRepository) GetByType(ctx context.Context, itemType string, limit, offset int) ([]domain.FlaggedItem, int64, error) {
	var items []domain.FlaggedItem
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("type = ?", itemType)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count flagged items for type %s: %w", itemType, err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&items)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list flagged items for type %s: %w", itemType, result.Error)
	}

	return items, total, nil
}

// UpdateStatus updates the status of a flagged item
func (r *FlaggedItemRepository) UpdateStatus(ctx context.Context, id, status, reviewedBy string) error {
	updates := map[string]interface{}{
		"status":      status,
		"reviewed_by": reviewedBy,
		"updated_at":  time.Now(),
	}

	if status != domain.StatusPending {
		now := time.Now()
		updates["reviewed_at"] = &now
	}

	result := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("id = ?", id).Updates(updates)
	if result.Error != nil {
		return fmt.Errorf("failed to update flagged item status: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("flagged item not found")
	}
	return nil
}

// GetWithOriginalData retrieves a flagged item with original data based on type
func (r *FlaggedItemRepository) GetWithOriginalData(ctx context.Context, id, itemType string) (*domain.FlaggedItem, interface{}, error) {
	// First get the flagged item
	item, err := r.GetByID(ctx, id)
	if err != nil {
		return nil, nil, err
	}

	// For now, we'll return the item with original data as nil
	// In a real implementation, this would query the appropriate table based on itemType
	// and use the DataID to fetch the original record
	var originalData interface{}

	// TODO: Implement actual data fetching based on itemType and DataID
	// This would involve querying tables like transactions, loan_requests, etc.
	// based on the itemType field and using the DataID to join

	return item, originalData, nil
}

// GetByReviewedBy retrieves flagged items reviewed by a specific user
func (r *FlaggedItemRepository) GetByReviewedBy(ctx context.Context, userID string, limit, offset int) ([]domain.FlaggedItem, int64, error) {
	var items []domain.FlaggedItem
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("reviewed_by = ?", userID)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count flagged items by reviewer: %w", err)
	}

	// Get items with pagination
	result := query.Order("reviewed_at DESC").Limit(limit).Offset(offset).Find(&items)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list flagged items by reviewer: %w", result.Error)
	}

	return items, total, nil
}

// UpdateClassification updates a flagged item with classification and notes
func (r *FlaggedItemRepository) UpdateClassification(ctx context.Context, id, status, reviewedBy, notes string) error {
	updates := map[string]interface{}{
		"status":       status,
		"reviewed_by":  reviewedBy,
		"review_notes": notes,
		"updated_at":   time.Now(),
	}

	if status != domain.StatusPending {
		now := time.Now()
		updates["reviewed_at"] = &now
	}

	result := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("id = ?", id).Updates(updates)
	if result.Error != nil {
		return fmt.Errorf("failed to update flagged item classification: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("flagged item not found")
	}
	return nil
}

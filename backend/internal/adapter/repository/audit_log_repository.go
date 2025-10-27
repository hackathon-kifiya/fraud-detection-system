package repository

import (
	"context"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

type AuditLogRepository struct {
	db *gorm.DB
}

// NewAuditLogRepository creates a new audit log repository
func NewAuditLogRepository(db *gorm.DB) port.AuditLogRepository {
	return &AuditLogRepository{db: db}
}

// Create creates a new audit log entry
func (r *AuditLogRepository) Create(ctx context.Context, log *domain.AuditLog) error {
	result := r.db.WithContext(ctx).Create(log)
	if result.Error != nil {
		return fmt.Errorf("failed to create audit log: %w", result.Error)
	}
	return nil
}

// GetByID retrieves an audit log entry by ID
func (r *AuditLogRepository) GetByID(ctx context.Context, id string) (*domain.AuditLog, error) {
	var log domain.AuditLog
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&log)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("audit log not found")
		}
		return nil, fmt.Errorf("failed to get audit log: %w", result.Error)
	}
	return &log, nil
}

// GetByFlaggedItemID retrieves all audit log entries for a flagged item
func (r *AuditLogRepository) GetByFlaggedItemID(ctx context.Context, flaggedItemID string) ([]domain.AuditLog, error) {
	var logs []domain.AuditLog
	result := r.db.WithContext(ctx).Where("flagged_item_id = ?", flaggedItemID).Order("timestamp ASC").Find(&logs)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to get audit logs by flagged item ID: %w", result.Error)
	}
	return logs, nil
}

// GetByUserID retrieves all audit log entries by a specific user
func (r *AuditLogRepository) GetByUserID(ctx context.Context, userID string, limit, offset int) ([]domain.AuditLog, int64, error) {
	var logs []domain.AuditLog
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.AuditLog{}).Where("user_id = ?", userID)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count audit logs by user ID: %w", err)
	}

	// Get items with pagination
	result := query.Order("timestamp DESC").Limit(limit).Offset(offset).Find(&logs)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list audit logs by user ID: %w", result.Error)
	}

	return logs, total, nil
}

// List retrieves audit log entries with pagination and filters
func (r *AuditLogRepository) List(ctx context.Context, limit, offset int, flaggedItemID, userID, action string) ([]domain.AuditLog, int64, error) {
	var logs []domain.AuditLog
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.AuditLog{})

	// Apply filters
	if flaggedItemID != "" {
		query = query.Where("flagged_item_id = ?", flaggedItemID)
	}
	if userID != "" {
		query = query.Where("user_id = ?", userID)
	}
	if action != "" {
		query = query.Where("action = ?", action)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count audit logs: %w", err)
	}

	// Get items with pagination
	result := query.Order("timestamp DESC").Limit(limit).Offset(offset).Find(&logs)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list audit logs: %w", result.Error)
	}

	return logs, total, nil
}

// GetStats retrieves audit statistics for a user
func (r *AuditLogRepository) GetStats(ctx context.Context, userID string) (*domain.AuditStats, error) {
	var stats domain.AuditStats

	// Get total reviewed count (items that have been reviewed by this user)
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("reviewed_by = ?", userID).Count(&stats.TotalReviewed).Error; err != nil {
		return nil, fmt.Errorf("failed to get total reviewed count: %w", err)
	}

	// Get confirmed fraud count
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("reviewed_by = ? AND status = ?", userID, domain.StatusConfirmed).Count(&stats.ConfirmedFraud).Error; err != nil {
		return nil, fmt.Errorf("failed to get confirmed fraud count: %w", err)
	}

	// Get false positives count
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("reviewed_by = ? AND status = ?", userID, domain.StatusFalsePositive).Count(&stats.FalsePositives).Error; err != nil {
		return nil, fmt.Errorf("failed to get false positives count: %w", err)
	}

	// Get pending review count
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("status = ?", domain.StatusPending).Count(&stats.PendingReview).Error; err != nil {
		return nil, fmt.Errorf("failed to get pending review count: %w", err)
	}

	// Get high risk items count (risk score > 80)
	if err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("risk_score > ?", 80).Count(&stats.HighRiskItems).Error; err != nil {
		return nil, fmt.Errorf("failed to get high risk items count: %w", err)
	}

	// Calculate average review time (simplified - time between created and reviewed)
	var avgReviewTime float64
	err := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).
		Select("COALESCE(AVG(EXTRACT(EPOCH FROM (reviewed_at - created_at))/60), 0)").
		Where("reviewed_by = ? AND reviewed_at IS NOT NULL", userID).
		Scan(&avgReviewTime).Error
	if err != nil {
		return nil, fmt.Errorf("failed to calculate average review time: %w", err)
	}
	stats.AverageReviewTime = int64(avgReviewTime)

	return &stats, nil
}

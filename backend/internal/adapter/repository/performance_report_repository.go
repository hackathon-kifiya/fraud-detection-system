package repository

import (
	"context"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

type PerformanceReportRepository struct {
	db *gorm.DB
}

// NewPerformanceReportRepository creates a new performance report repository
func NewPerformanceReportRepository(db *gorm.DB) port.PerformanceReportRepository {
	return &PerformanceReportRepository{db: db}
}

// Create creates a new performance report
func (r *PerformanceReportRepository) Create(ctx context.Context, report *domain.PerformanceReport) error {
	result := r.db.WithContext(ctx).Create(report)
	if result.Error != nil {
		return fmt.Errorf("failed to create performance report: %w", result.Error)
	}
	return nil
}

// GetByID retrieves a performance report by ID
func (r *PerformanceReportRepository) GetByID(ctx context.Context, id string) (*domain.PerformanceReport, error) {
	var report domain.PerformanceReport
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&report)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("performance report not found")
		}
		return nil, fmt.Errorf("failed to get performance report: %w", result.Error)
	}
	return &report, nil
}

// List retrieves performance reports with pagination and filters
func (r *PerformanceReportRepository) List(ctx context.Context, limit, offset int, reportType, generatedBy string) ([]domain.PerformanceReport, int64, error) {
	var reports []domain.PerformanceReport
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.PerformanceReport{})

	// Apply filters
	if reportType != "" {
		query = query.Where("report_type = ?", reportType)
	}
	if generatedBy != "" {
		query = query.Where("generated_by = ?", generatedBy)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count performance reports: %w", err)
	}

	// Get items with pagination
	result := query.Order("generated_at DESC").Limit(limit).Offset(offset).Find(&reports)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list performance reports: %w", result.Error)
	}

	return reports, total, nil
}

// GetByDateRange retrieves reports within a date range
func (r *PerformanceReportRepository) GetByDateRange(ctx context.Context, startDate, endDate time.Time) ([]domain.PerformanceReport, error) {
	var reports []domain.PerformanceReport
	result := r.db.WithContext(ctx).
		Where("start_date >= ? AND end_date <= ?", startDate, endDate).
		Order("generated_at DESC").
		Find(&reports)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to get performance reports by date range: %w", result.Error)
	}

	return reports, nil
}

// Update updates a performance report
func (r *PerformanceReportRepository) Update(ctx context.Context, report *domain.PerformanceReport) error {
	result := r.db.WithContext(ctx).Save(report)
	if result.Error != nil {
		return fmt.Errorf("failed to update performance report: %w", result.Error)
	}
	return nil
}

// Delete deletes a performance report
func (r *PerformanceReportRepository) Delete(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Delete(&domain.PerformanceReport{}, "id = ?", id)
	if result.Error != nil {
		return fmt.Errorf("failed to delete performance report: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("performance report not found")
	}
	return nil
}

// GetLatestByType retrieves the latest report of a specific type
func (r *PerformanceReportRepository) GetLatestByType(ctx context.Context, reportType string) (*domain.PerformanceReport, error) {
	var report domain.PerformanceReport
	result := r.db.WithContext(ctx).
		Where("report_type = ?", reportType).
		Order("generated_at DESC").
		First(&report)

	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("performance report not found")
		}
		return nil, fmt.Errorf("failed to get latest performance report: %w", result.Error)
	}

	return &report, nil
}

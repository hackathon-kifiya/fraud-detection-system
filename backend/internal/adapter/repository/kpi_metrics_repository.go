package repository

import (
	"context"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

type KPIMetricsRepository struct {
	db *gorm.DB
}

// NewKPIMetricsRepository creates a new KPI metrics repository
func NewKPIMetricsRepository(db *gorm.DB) port.KPIMetricsRepository {
	return &KPIMetricsRepository{db: db}
}

// Create creates a new KPI metric entry
func (r *KPIMetricsRepository) Create(ctx context.Context, metric *domain.KPIMetrics) error {
	result := r.db.WithContext(ctx).Create(metric)
	if result.Error != nil {
		return fmt.Errorf("failed to create KPI metric: %w", result.Error)
	}
	return nil
}

// GetByID retrieves a KPI metric by ID
func (r *KPIMetricsRepository) GetByID(ctx context.Context, id string) (*domain.KPIMetrics, error) {
	var metric domain.KPIMetrics
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&metric)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("KPI metric not found")
		}
		return nil, fmt.Errorf("failed to get KPI metric: %w", result.Error)
	}
	return &metric, nil
}

// GetLatest retrieves the latest metrics for all metric names
func (r *KPIMetricsRepository) GetLatest(ctx context.Context) ([]domain.KPIMetrics, error) {
	var metrics []domain.KPIMetrics

	// Get the latest metric for each metric name
	result := r.db.WithContext(ctx).
		Raw(`
			SELECT DISTINCT ON (metric_name) id, metric_name, metric_value, calculated_at, metadata
			FROM kpi_metrics 
			ORDER BY metric_name, calculated_at DESC
		`).
		Scan(&metrics)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to get latest KPI metrics: %w", result.Error)
	}

	return metrics, nil
}

// GetByMetricName retrieves metrics by name with pagination
func (r *KPIMetricsRepository) GetByMetricName(ctx context.Context, metricName string, limit, offset int) ([]domain.KPIMetrics, int64, error) {
	var metrics []domain.KPIMetrics
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.KPIMetrics{}).Where("metric_name = ?", metricName)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count KPI metrics: %w", err)
	}

	// Get items with pagination
	result := query.Order("calculated_at DESC").Limit(limit).Offset(offset).Find(&metrics)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to get KPI metrics: %w", result.Error)
	}

	return metrics, total, nil
}

// GetByDateRange retrieves metrics within a date range
func (r *KPIMetricsRepository) GetByDateRange(ctx context.Context, startDate, endDate time.Time) ([]domain.KPIMetrics, error) {
	var metrics []domain.KPIMetrics
	result := r.db.WithContext(ctx).
		Where("calculated_at >= ? AND calculated_at <= ?", startDate, endDate).
		Order("calculated_at ASC").
		Find(&metrics)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to get KPI metrics by date range: %w", result.Error)
	}

	return metrics, nil
}

// GetTrends retrieves trend data for specific metrics
func (r *KPIMetricsRepository) GetTrends(ctx context.Context, metricNames []string, days int) (map[string][]domain.KPIMetrics, error) {
	trends := make(map[string][]domain.KPIMetrics)
	cutoff := time.Now().AddDate(0, 0, -days)

	for _, metricName := range metricNames {
		var metrics []domain.KPIMetrics
		result := r.db.WithContext(ctx).
			Where("metric_name = ? AND calculated_at >= ?", metricName, cutoff).
			Order("calculated_at ASC").
			Find(&metrics)

		if result.Error != nil {
			return nil, fmt.Errorf("failed to get trend data for metric %s: %w", metricName, result.Error)
		}

		trends[metricName] = metrics
	}

	return trends, nil
}

// Delete deletes old metrics (for cleanup)
func (r *KPIMetricsRepository) Delete(ctx context.Context, olderThan time.Time) error {
	result := r.db.WithContext(ctx).Delete(&domain.KPIMetrics{}, "calculated_at < ?", olderThan)
	if result.Error != nil {
		return fmt.Errorf("failed to delete old KPI metrics: %w", result.Error)
	}
	return nil
}

// GetAggregatedMetrics retrieves aggregated metrics for dashboard
func (r *KPIMetricsRepository) GetAggregatedMetrics(ctx context.Context) (*domain.KPIMetricsResponse, error) {
	// Get latest metrics for each type
	latestMetrics, err := r.GetLatest(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get latest metrics: %w", err)
	}

	response := &domain.KPIMetricsResponse{
		CalculatedAt: time.Now(),
	}

	// Map metrics to response fields
	for _, metric := range latestMetrics {
		switch metric.MetricName {
		case domain.MetricFalsePositiveRate:
			response.FalsePositiveRate = metric.MetricValue
		case domain.MetricFalseNegativeRate:
			response.FalseNegativeRate = metric.MetricValue
		case domain.MetricAccuracy:
			response.Accuracy = metric.MetricValue
		case domain.MetricPrecision:
			response.Precision = metric.MetricValue
		case domain.MetricRecall:
			response.Recall = metric.MetricValue
		case domain.MetricF1Score:
			response.F1Score = metric.MetricValue
		case domain.MetricThroughput:
			response.Throughput = metric.MetricValue
		case domain.MetricAvgReviewTime:
			response.AvgReviewTime = metric.MetricValue
		}
	}

	return response, nil
}

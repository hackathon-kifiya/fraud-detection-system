package port

import (
	"context"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
)

// SystemConfigRepository defines the interface for system configuration repository operations
type SystemConfigRepository interface {
	// Create creates a new system configuration
	Create(ctx context.Context, config *domain.SystemConfig) error

	// GetByKey retrieves a system configuration by key
	GetByKey(ctx context.Context, key string) (*domain.SystemConfig, error)

	// GetAll retrieves all system configurations
	GetAll(ctx context.Context) ([]domain.SystemConfig, error)

	// Update updates a system configuration
	Update(ctx context.Context, config *domain.SystemConfig) error

	// Delete deletes a system configuration
	Delete(ctx context.Context, key string) error

	// GetByType retrieves configurations by type
	GetByType(ctx context.Context, configType string) ([]domain.SystemConfig, error)

	// GetHistory retrieves configuration change history
	GetHistory(ctx context.Context, key string, limit, offset int) ([]domain.SystemConfig, int64, error)
}

// CaseAssignmentRepository defines the interface for case assignment repository operations
type CaseAssignmentRepository interface {
	// Create creates a new case assignment
	Create(ctx context.Context, assignment *domain.CaseAssignment) error

	// GetByID retrieves a case assignment by ID
	GetByID(ctx context.Context, id string) (*domain.CaseAssignment, error)

	// GetByFlaggedItemID retrieves assignment for a flagged item
	GetByFlaggedItemID(ctx context.Context, flaggedItemID string) (*domain.CaseAssignment, error)

	// GetByAuditorID retrieves assignments for an auditor with optional status filter
	GetByAuditorID(ctx context.Context, auditorID string, limit, offset int, status string) ([]domain.CaseAssignment, int64, error)

	// List retrieves case assignments with pagination and filters
	List(ctx context.Context, limit, offset int, status, priority string) ([]domain.CaseAssignment, int64, error)

	// Update updates a case assignment
	Update(ctx context.Context, assignment *domain.CaseAssignment) error

	// Delete deletes a case assignment
	Delete(ctx context.Context, id string) error

	// GetUnassignedCases retrieves flagged items without assignments
	GetUnassignedCases(ctx context.Context, limit, offset int) ([]domain.FlaggedItem, int64, error)

	// GetAuditorWorkload retrieves workload distribution for all auditors
	GetAuditorWorkload(ctx context.Context) ([]domain.AuditorWorkloadResponse, error)

	// GetOverdueAssignments retrieves overdue assignments
	GetOverdueAssignments(ctx context.Context) ([]domain.CaseAssignment, error)
}

// PerformanceReportRepository defines the interface for performance report repository operations
type PerformanceReportRepository interface {
	// Create creates a new performance report
	Create(ctx context.Context, report *domain.PerformanceReport) error

	// GetByID retrieves a performance report by ID
	GetByID(ctx context.Context, id string) (*domain.PerformanceReport, error)

	// List retrieves performance reports with pagination and filters
	List(ctx context.Context, limit, offset int, reportType, generatedBy string) ([]domain.PerformanceReport, int64, error)

	// GetByDateRange retrieves reports within a date range
	GetByDateRange(ctx context.Context, startDate, endDate time.Time) ([]domain.PerformanceReport, error)

	// Update updates a performance report
	Update(ctx context.Context, report *domain.PerformanceReport) error

	// Delete deletes a performance report
	Delete(ctx context.Context, id string) error

	// GetLatestByType retrieves the latest report of a specific type
	GetLatestByType(ctx context.Context, reportType string) (*domain.PerformanceReport, error)
}

// KPIMetricsRepository defines the interface for KPI metrics repository operations
type KPIMetricsRepository interface {
	// Create creates a new KPI metric entry
	Create(ctx context.Context, metric *domain.KPIMetrics) error

	// GetByID retrieves a KPI metric by ID
	GetByID(ctx context.Context, id string) (*domain.KPIMetrics, error)

	// GetLatest retrieves the latest metrics for all metric names
	GetLatest(ctx context.Context) ([]domain.KPIMetrics, error)

	// GetByMetricName retrieves metrics by name with pagination
	GetByMetricName(ctx context.Context, metricName string, limit, offset int) ([]domain.KPIMetrics, int64, error)

	// GetByDateRange retrieves metrics within a date range
	GetByDateRange(ctx context.Context, startDate, endDate time.Time) ([]domain.KPIMetrics, error)

	// GetTrends retrieves trend data for specific metrics
	GetTrends(ctx context.Context, metricNames []string, days int) (map[string][]domain.KPIMetrics, error)

	// Delete deletes old metrics (for cleanup)
	Delete(ctx context.Context, olderThan time.Time) error

	// GetAggregatedMetrics retrieves aggregated metrics for dashboard
	GetAggregatedMetrics(ctx context.Context) (*domain.KPIMetricsResponse, error)
}

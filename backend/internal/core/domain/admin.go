package domain

import (
	"time"
)

// SystemConfig represents system-wide configuration settings
type SystemConfig struct {
	ID          string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	ConfigKey   string    `json:"config_key" gorm:"uniqueIndex;not null"`
	ConfigValue string    `json:"config_value" gorm:"not null"`
	ConfigType  string    `json:"config_type" gorm:"not null"` // string, number, boolean, json
	Description string    `json:"description" gorm:"type:text"`
	UpdatedBy   string    `json:"updated_by" gorm:"not null"`
	UpdatedAt   time.Time `json:"updated_at" gorm:"autoUpdateTime"`
	CreatedAt   time.Time `json:"created_at" gorm:"autoCreateTime"`
}

// TableName specifies the table name for GORM
func (SystemConfig) TableName() string {
	return "system_config"
}

// CaseAssignment represents case assignment to auditors
type CaseAssignment struct {
	ID            string     `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	FlaggedItemID string     `json:"flagged_item_id" gorm:"not null"`
	AuditorID     string     `json:"auditor_id" gorm:"not null"`
	AssignedBy    string     `json:"assigned_by" gorm:"not null"`
	AssignedAt    time.Time  `json:"assigned_at" gorm:"autoCreateTime"`
	Status        string     `json:"status" gorm:"not null;default:'assigned'"` // assigned, in_progress, completed, cancelled
	Priority      string     `json:"priority" gorm:"not null;default:'medium'"` // low, medium, high, urgent
	DueDate       *time.Time `json:"due_date" gorm:"column:due_date"`
	Notes         string     `json:"notes" gorm:"type:text"`
	CreatedAt     time.Time  `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt     time.Time  `json:"updated_at" gorm:"autoUpdateTime"`
}

// TableName specifies the table name for GORM
func (CaseAssignment) TableName() string {
	return "case_assignments"
}

// CaseAssignmentStatus constants
const (
	AssignmentStatusAssigned   = "assigned"
	AssignmentStatusInProgress = "in_progress"
	AssignmentStatusCompleted  = "completed"
	AssignmentStatusCancelled  = "cancelled"
)

// CaseAssignmentPriority constants
const (
	PriorityLow    = "low"
	PriorityMedium = "medium"
	PriorityHigh   = "high"
	PriorityUrgent = "urgent"
)

// PerformanceReport represents generated performance reports
type PerformanceReport struct {
	ID          string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	ReportType  string    `json:"report_type" gorm:"not null"`
	StartDate   time.Time `json:"start_date" gorm:"not null"`
	EndDate     time.Time `json:"end_date" gorm:"not null"`
	ReportData  string    `json:"report_data" gorm:"type:jsonb"`
	GeneratedBy string    `json:"generated_by" gorm:"not null"`
	GeneratedAt time.Time `json:"generated_at" gorm:"autoCreateTime"`
}

// TableName specifies the table name for GORM
func (PerformanceReport) TableName() string {
	return "performance_reports"
}

// ReportType constants
const (
	ReportTypeSystemThroughput   = "system_throughput"
	ReportTypeAuditorPerformance = "auditor_performance"
	ReportTypeModelPerformance   = "model_performance"
	ReportTypeTimeBasedAnalysis  = "time_based_analysis"
	ReportTypeTypeBasedAnalysis  = "type_based_analysis"
)

// KPIMetrics represents KPI metric tracking
type KPIMetrics struct {
	ID           string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	MetricName   string    `json:"metric_name" gorm:"not null"`
	MetricValue  float64   `json:"metric_value" gorm:"not null"`
	CalculatedAt time.Time `json:"calculated_at" gorm:"autoCreateTime"`
	Metadata     string    `json:"metadata" gorm:"type:jsonb"`
}

// TableName specifies the table name for GORM
func (KPIMetrics) TableName() string {
	return "kpi_metrics"
}

// KPI Metric Names
const (
	MetricFalsePositiveRate = "false_positive_rate"
	MetricFalseNegativeRate = "false_negative_rate"
	MetricAccuracy          = "accuracy"
	MetricPrecision         = "precision"
	MetricRecall            = "recall"
	MetricF1Score           = "f1_score"
	MetricThroughput        = "throughput"
	MetricAvgReviewTime     = "avg_review_time"
)

// SystemPerformanceStats represents system-wide performance statistics
type SystemPerformanceStats struct {
	TotalTransactions int64            `json:"total_transactions"`
	ProcessedItems    int64            `json:"processed_items"`
	ApprovedItems     int64            `json:"approved_items"`
	BlockedItems      int64            `json:"blocked_items"`
	PendingReview     int64            `json:"pending_review"`
	ApprovalRate      float64          `json:"approval_rate"`
	BlockRate         float64          `json:"block_rate"`
	AvgProcessingTime float64          `json:"avg_processing_time_minutes"`
	ThroughputPerHour float64          `json:"throughput_per_hour"`
	PerformanceByType map[string]int64 `json:"performance_by_type"`
	TimeRange         struct {
		StartDate time.Time `json:"start_date"`
		EndDate   time.Time `json:"end_date"`
	} `json:"time_range"`
}

// AuditorPerformanceReport represents individual auditor performance
type AuditorPerformanceReport struct {
	AuditorID            string     `json:"auditor_id"`
	AuditorName          string     `json:"auditor_name"`
	TotalReviewed        int64      `json:"total_reviewed"`
	ConfirmedFraud       int64      `json:"confirmed_fraud"`
	FalsePositives       int64      `json:"false_positives"`
	AvgReviewTime        float64    `json:"avg_review_time_minutes"`
	Accuracy             float64    `json:"accuracy"`
	Efficiency           float64    `json:"efficiency_score"`
	LastReviewAt         *time.Time `json:"last_review_at"`
	ActiveAssignments    int64      `json:"active_assignments"`
	CompletedAssignments int64      `json:"completed_assignments"`
	TimeRange            struct {
		StartDate time.Time `json:"start_date"`
		EndDate   time.Time `json:"end_date"`
	} `json:"time_range"`
}

// RiskThresholdConfig represents risk threshold configuration
type RiskThresholdConfig struct {
	AutoApproveThreshold float64   `json:"auto_approve_threshold"`
	HumanReviewThreshold float64   `json:"human_review_threshold"`
	AutoBlockThreshold   float64   `json:"auto_block_threshold"`
	HighRiskThreshold    float64   `json:"high_risk_threshold"`
	UpdatedBy            string    `json:"updated_by"`
	UpdatedAt            time.Time `json:"updated_at"`
}

// Request/Response Types

// GenerateReportRequest represents request to generate performance report
type GenerateReportRequest struct {
	ReportType string    `json:"report_type" binding:"required"`
	StartDate  time.Time `json:"start_date" binding:"required"`
	EndDate    time.Time `json:"end_date" binding:"required"`
	Format     string    `json:"format"` // json, csv, pdf
}

// UpdateRiskThresholdRequest represents request to update risk thresholds
type UpdateRiskThresholdRequest struct {
	AutoApproveThreshold *float64 `json:"auto_approve_threshold,omitempty"`
	HumanReviewThreshold *float64 `json:"human_review_threshold,omitempty"`
	AutoBlockThreshold   *float64 `json:"auto_block_threshold,omitempty"`
	HighRiskThreshold    *float64 `json:"high_risk_threshold,omitempty"`
}

// AssignCaseRequest represents request to assign case to auditor
type AssignCaseRequest struct {
	FlaggedItemID string     `json:"flagged_item_id" binding:"required"`
	AuditorID     string     `json:"auditor_id" binding:"required"`
	Priority      string     `json:"priority" binding:"required,oneof=low medium high urgent"`
	DueDate       *time.Time `json:"due_date"`
	Notes         string     `json:"notes"`
}

// BulkAssignCasesRequest represents request for bulk case assignment
type BulkAssignCasesRequest struct {
	FlaggedItemIDs []string   `json:"flagged_item_ids" binding:"required"`
	AuditorID      string     `json:"auditor_id" binding:"required"`
	Priority       string     `json:"priority" binding:"required,oneof=low medium high urgent"`
	DueDate        *time.Time `json:"due_date"`
	Notes          string     `json:"notes"`
}

// UpdateAssignmentRequest represents request to update case assignment
type UpdateAssignmentRequest struct {
	Status   *string    `json:"status,omitempty" binding:"omitempty,oneof=assigned in_progress completed cancelled"`
	Priority *string    `json:"priority,omitempty" binding:"omitempty,oneof=low medium high urgent"`
	DueDate  *time.Time `json:"due_date,omitempty"`
	Notes    *string    `json:"notes,omitempty"`
}

// KPIMetricsResponse represents KPI metrics response
type KPIMetricsResponse struct {
	FalsePositiveRate float64   `json:"false_positive_rate"`
	FalseNegativeRate float64   `json:"false_negative_rate"`
	Accuracy          float64   `json:"accuracy"`
	Precision         float64   `json:"precision"`
	Recall            float64   `json:"recall"`
	F1Score           float64   `json:"f1_score"`
	Throughput        float64   `json:"throughput"`
	AvgReviewTime     float64   `json:"avg_review_time_minutes"`
	CalculatedAt      time.Time `json:"calculated_at"`
}

// AuditorWorkloadResponse represents auditor workload distribution
type AuditorWorkloadResponse struct {
	AuditorID         string  `json:"auditor_id"`
	AuditorName       string  `json:"auditor_name"`
	ActiveAssignments int64   `json:"active_assignments"`
	CompletedToday    int64   `json:"completed_today"`
	CompletedThisWeek int64   `json:"completed_this_week"`
	AvgReviewTime     float64 `json:"avg_review_time_minutes"`
	Efficiency        float64 `json:"efficiency_score"`
	IsAvailable       bool    `json:"is_available"`
}

// SystemOverviewResponse represents system overview analytics
type SystemOverviewResponse struct {
	SystemStats  SystemPerformanceStats `json:"system_stats"`
	KPIMetrics   KPIMetricsResponse     `json:"kpi_metrics"`
	AuditorStats struct {
		TotalAuditors        int64   `json:"total_auditors"`
		ActiveAuditors       int64   `json:"active_auditors"`
		AvgWorkload          float64 `json:"avg_workload"`
		MostEfficientAuditor string  `json:"most_efficient_auditor"`
	} `json:"auditor_stats"`
	RecentActivity []struct {
		Action      string    `json:"action"`
		Description string    `json:"description"`
		Timestamp   time.Time `json:"timestamp"`
		UserID      string    `json:"user_id"`
	} `json:"recent_activity"`
}

// TrendAnalysisResponse represents trend analysis over time
type TrendAnalysisResponse struct {
	TimeRange struct {
		StartDate time.Time `json:"start_date"`
		EndDate   time.Time `json:"end_date"`
	} `json:"time_range"`
	Trends struct {
		TransactionVolume []struct {
			Date  time.Time `json:"date"`
			Count int64     `json:"count"`
		} `json:"transaction_volume"`
		ApprovalRate []struct {
			Date time.Time `json:"date"`
			Rate float64   `json:"rate"`
		} `json:"approval_rate"`
		FalsePositiveRate []struct {
			Date time.Time `json:"date"`
			Rate float64   `json:"rate"`
		} `json:"false_positive_rate"`
		AuditorEfficiency []struct {
			Date  time.Time `json:"date"`
			Score float64   `json:"score"`
		} `json:"auditor_efficiency"`
	} `json:"trends"`
}

// ThroughputMetricsResponse represents transaction throughput metrics
type ThroughputMetricsResponse struct {
	TimeRange struct {
		StartDate time.Time `json:"start_date"`
		EndDate   time.Time `json:"end_date"`
	} `json:"time_range"`
	Throughput struct {
		TotalProcessed    int64   `json:"total_processed"`
		PerHour           float64 `json:"per_hour"`
		PerDay            float64 `json:"per_day"`
		PeakHour          string  `json:"peak_hour"`
		PeakDay           string  `json:"peak_day"`
		AvgProcessingTime float64 `json:"avg_processing_time_minutes"`
	} `json:"throughput"`
	Breakdown struct {
		ByType map[string]int64 `json:"by_type"`
		ByHour map[string]int64 `json:"by_hour"`
		ByDay  map[string]int64 `json:"by_day"`
	} `json:"breakdown"`
}

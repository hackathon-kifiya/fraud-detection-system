package service

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

type AdminService struct {
	flaggedItemRepo       port.FlaggedItemRepository
	auditLogRepo          port.AuditLogRepository
	systemConfigRepo      port.SystemConfigRepository
	caseAssignmentRepo    port.CaseAssignmentRepository
	performanceReportRepo port.PerformanceReportRepository
	kpiMetricsRepo        port.KPIMetricsRepository
	userRepo              port.UserRepository
}

// NewAdminService creates a new admin service
func NewAdminService(
	flaggedItemRepo port.FlaggedItemRepository,
	auditLogRepo port.AuditLogRepository,
	systemConfigRepo port.SystemConfigRepository,
	caseAssignmentRepo port.CaseAssignmentRepository,
	performanceReportRepo port.PerformanceReportRepository,
	kpiMetricsRepo port.KPIMetricsRepository,
	userRepo port.UserRepository,
) *AdminService {
	return &AdminService{
		flaggedItemRepo:       flaggedItemRepo,
		auditLogRepo:          auditLogRepo,
		systemConfigRepo:      systemConfigRepo,
		caseAssignmentRepo:    caseAssignmentRepo,
		performanceReportRepo: performanceReportRepo,
		kpiMetricsRepo:        kpiMetricsRepo,
		userRepo:              userRepo,
	}
}

// GeneratePerformanceReport generates a system performance report
func (s *AdminService) GeneratePerformanceReport(ctx context.Context, req domain.GenerateReportRequest, generatedBy string) (*domain.PerformanceReport, error) {
	var reportData interface{}

	switch req.ReportType {
	case domain.ReportTypeSystemThroughput:
		reportData, _ = s.generateSystemThroughputReport(ctx, req.StartDate, req.EndDate)
	case domain.ReportTypeAuditorPerformance:
		reportData, _ = s.generateAuditorPerformanceReport(ctx, req.StartDate, req.EndDate)
	case domain.ReportTypeModelPerformance:
		reportData, _ = s.generateModelPerformanceReport(ctx, req.StartDate, req.EndDate)
	case domain.ReportTypeTimeBasedAnalysis:
		reportData, _ = s.generateTimeBasedAnalysisReport(ctx, req.StartDate, req.EndDate)
	case domain.ReportTypeTypeBasedAnalysis:
		reportData, _ = s.generateTypeBasedAnalysisReport(ctx, req.StartDate, req.EndDate)
	default:
		return nil, fmt.Errorf("unsupported report type: %s", req.ReportType)
	}

	// Convert report data to JSON
	reportDataJSON, err := json.Marshal(reportData)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal report data: %w", err)
	}

	// Create performance report
	report := &domain.PerformanceReport{
		ReportType:  req.ReportType,
		StartDate:   req.StartDate,
		EndDate:     req.EndDate,
		ReportData:  string(reportDataJSON),
		GeneratedBy: generatedBy,
		GeneratedAt: time.Now(),
	}

	err = s.performanceReportRepo.Create(ctx, report)
	if err != nil {
		return nil, fmt.Errorf("failed to create performance report: %w", err)
	}

	return report, nil
}

// GetKPIMetrics calculates and returns real-time KPI metrics
func (s *AdminService) GetKPIMetrics(ctx context.Context) (*domain.KPIMetricsResponse, error) {
	// Get aggregated metrics from repository
	metrics, err := s.kpiMetricsRepo.GetAggregatedMetrics(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get aggregated metrics: %w", err)
	}

	// If no metrics exist, calculate them
	if metrics.FalsePositiveRate == 0 && metrics.Accuracy == 0 {
		// Calculate KPIs from flagged items
		calculatedMetrics, err := s.calculateKPIs(ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to calculate KPIs: %w", err)
		}

		// Store calculated metrics
		for metricName, value := range calculatedMetrics {
			metric := &domain.KPIMetrics{
				MetricName:   metricName,
				MetricValue:  value,
				CalculatedAt: time.Now(),
			}
			s.kpiMetricsRepo.Create(ctx, metric)
		}

		// Return calculated metrics
		return &domain.KPIMetricsResponse{
			FalsePositiveRate: calculatedMetrics[domain.MetricFalsePositiveRate],
			FalseNegativeRate: calculatedMetrics[domain.MetricFalseNegativeRate],
			Accuracy:          calculatedMetrics[domain.MetricAccuracy],
			Precision:         calculatedMetrics[domain.MetricPrecision],
			Recall:            calculatedMetrics[domain.MetricRecall],
			F1Score:           calculatedMetrics[domain.MetricF1Score],
			Throughput:        calculatedMetrics[domain.MetricThroughput],
			AvgReviewTime:     calculatedMetrics[domain.MetricAvgReviewTime],
			CalculatedAt:      time.Now(),
		}, nil
	}

	return metrics, nil
}

// GetAuditorPerformance gets performance metrics for a specific auditor
func (s *AdminService) GetAuditorPerformance(ctx context.Context, auditorID string, startDate, endDate time.Time) (*domain.AuditorPerformanceReport, error) {
	// Get auditor info
	auditor, err := s.userRepo.GetByID(ctx, auditorID)
	if err != nil {
		return nil, fmt.Errorf("auditor not found: %w", err)
	}

	// Get auditor's reviewed items in date range
	// This would need to be implemented in the flagged item repository
	// For now, return a placeholder
	report := &domain.AuditorPerformanceReport{
		AuditorID:            auditorID,
		AuditorName:          fmt.Sprintf("%s %s", auditor.FirstName, auditor.LastName),
		TotalReviewed:        0, // TODO: Calculate from flagged items
		ConfirmedFraud:       0, // TODO: Calculate from flagged items
		FalsePositives:       0, // TODO: Calculate from flagged items
		AvgReviewTime:        0, // TODO: Calculate from audit logs
		Accuracy:             0, // TODO: Calculate accuracy
		Efficiency:           0, // TODO: Calculate efficiency score
		LastReviewAt:         nil,
		ActiveAssignments:    0, // TODO: Calculate from case assignments
		CompletedAssignments: 0, // TODO: Calculate from case assignments
		TimeRange: struct {
			StartDate time.Time `json:"start_date"`
			EndDate   time.Time `json:"end_date"`
		}{
			StartDate: startDate,
			EndDate:   endDate,
		},
	}

	return report, nil
}

// GetAllAuditorsPerformance gets performance metrics for all auditors
func (s *AdminService) GetAllAuditorsPerformance(ctx context.Context, startDate, endDate time.Time) ([]domain.AuditorPerformanceReport, error) {
	// Get all auditors
	// This would need to be implemented in the user repository
	// For now, return empty slice
	var reports []domain.AuditorPerformanceReport

	// TODO: Implement actual auditor performance calculation
	// 1. Get all users with role 'analyst'
	// 2. For each auditor, calculate their performance metrics
	// 3. Return list of performance reports

	return reports, nil
}

// UpdateRiskThreshold updates risk thresholds
func (s *AdminService) UpdateRiskThreshold(ctx context.Context, req domain.UpdateRiskThresholdRequest, updatedBy string) error {
	thresholds := map[string]*float64{
		"auto_approve_threshold": req.AutoApproveThreshold,
		"human_review_threshold": req.HumanReviewThreshold,
		"auto_block_threshold":   req.AutoBlockThreshold,
		"high_risk_threshold":    req.HighRiskThreshold,
	}

	for key, value := range thresholds {
		if value != nil {
			config := &domain.SystemConfig{
				ConfigKey:   key,
				ConfigValue: fmt.Sprintf("%.2f", *value),
				ConfigType:  "number",
				Description: fmt.Sprintf("Risk threshold for %s", key),
				UpdatedBy:   updatedBy,
			}

			// Check if config exists
			existing, err := s.systemConfigRepo.GetByKey(ctx, key)
			if err != nil {
				// Create new config
				err = s.systemConfigRepo.Create(ctx, config)
			} else {
				// Update existing config
				existing.ConfigValue = config.ConfigValue
				existing.UpdatedBy = updatedBy
				err = s.systemConfigRepo.Update(ctx, existing)
			}

			if err != nil {
				return fmt.Errorf("failed to update threshold %s: %w", key, err)
			}
		}
	}

	return nil
}

// GetRiskThresholds retrieves current risk thresholds
func (s *AdminService) GetRiskThresholds(ctx context.Context) (*domain.RiskThresholdConfig, error) {
	thresholds := &domain.RiskThresholdConfig{}

	// Get each threshold
	keys := []string{"auto_approve_threshold", "human_review_threshold", "auto_block_threshold", "high_risk_threshold"}

	for _, key := range keys {
		config, err := s.systemConfigRepo.GetByKey(ctx, key)
		if err == nil {
			// Parse the value based on key
			switch key {
			case "auto_approve_threshold":
				fmt.Sscanf(config.ConfigValue, "%f", &thresholds.AutoApproveThreshold)
			case "human_review_threshold":
				fmt.Sscanf(config.ConfigValue, "%f", &thresholds.HumanReviewThreshold)
			case "auto_block_threshold":
				fmt.Sscanf(config.ConfigValue, "%f", &thresholds.AutoBlockThreshold)
			case "high_risk_threshold":
				fmt.Sscanf(config.ConfigValue, "%f", &thresholds.HighRiskThreshold)
			}
			thresholds.UpdatedBy = config.UpdatedBy
			thresholds.UpdatedAt = config.UpdatedAt
		}
	}

	return thresholds, nil
}

// AssignCase assigns a case to an auditor
func (s *AdminService) AssignCase(ctx context.Context, req domain.AssignCaseRequest, assignedBy string) (*domain.CaseAssignment, error) {
	// Check if flagged item exists
	_, err := s.flaggedItemRepo.GetByID(ctx, req.FlaggedItemID)
	if err != nil {
		return nil, fmt.Errorf("flagged item not found: %w", err)
	}

	// Check if auditor exists
	_, err = s.userRepo.GetByID(ctx, req.AuditorID)
	if err != nil {
		return nil, fmt.Errorf("auditor not found: %w", err)
	}

	// Check if case is already assigned
	existing, err := s.caseAssignmentRepo.GetByFlaggedItemID(ctx, req.FlaggedItemID)
	if err == nil && existing != nil {
		return nil, fmt.Errorf("case is already assigned to auditor %s", existing.AuditorID)
	}

	// Create assignment
	assignment := &domain.CaseAssignment{
		FlaggedItemID: req.FlaggedItemID,
		AuditorID:     req.AuditorID,
		AssignedBy:    assignedBy,
		Status:        domain.AssignmentStatusAssigned,
		Priority:      req.Priority,
		DueDate:       req.DueDate,
		Notes:         req.Notes,
	}

	err = s.caseAssignmentRepo.Create(ctx, assignment)
	if err != nil {
		return nil, fmt.Errorf("failed to create case assignment: %w", err)
	}

	return assignment, nil
}

// BulkAssignCases assigns multiple cases to an auditor
func (s *AdminService) BulkAssignCases(ctx context.Context, req domain.BulkAssignCasesRequest, assignedBy string) ([]domain.CaseAssignment, error) {
	var assignments []domain.CaseAssignment

	for _, flaggedItemID := range req.FlaggedItemIDs {
		assignment := &domain.CaseAssignment{
			FlaggedItemID: flaggedItemID,
			AuditorID:     req.AuditorID,
			AssignedBy:    assignedBy,
			Status:        domain.AssignmentStatusAssigned,
			Priority:      req.Priority,
			DueDate:       req.DueDate,
			Notes:         req.Notes,
		}

		err := s.caseAssignmentRepo.Create(ctx, assignment)
		if err != nil {
			// Log error but continue with other assignments
			fmt.Printf("Warning: failed to assign case %s: %v\n", flaggedItemID, err)
			continue
		}

		assignments = append(assignments, *assignment)
	}

	return assignments, nil
}

// GetUnassignedCases gets cases pending assignment
func (s *AdminService) GetUnassignedCases(ctx context.Context, limit, offset int) ([]domain.FlaggedItem, int64, error) {
	return s.caseAssignmentRepo.GetUnassignedCases(ctx, limit, offset)
}

// GetAuditorWorkload gets current workload per auditor
func (s *AdminService) GetAuditorWorkload(ctx context.Context) ([]domain.AuditorWorkloadResponse, error) {
	return s.caseAssignmentRepo.GetAuditorWorkload(ctx)
}

// Helper methods for report generation

func (s *AdminService) generateSystemThroughputReport(ctx context.Context, startDate, endDate time.Time) (*domain.SystemPerformanceStats, error) {
	// TODO: Implement actual system throughput calculation
	// This would query flagged items and calculate metrics
	return &domain.SystemPerformanceStats{}, nil
}

func (s *AdminService) generateAuditorPerformanceReport(ctx context.Context, startDate, endDate time.Time) ([]domain.AuditorPerformanceReport, error) {
	// TODO: Implement actual auditor performance calculation
	return []domain.AuditorPerformanceReport{}, nil
}

func (s *AdminService) generateModelPerformanceReport(ctx context.Context, startDate, endDate time.Time) (map[string]interface{}, error) {
	// TODO: Implement actual model performance calculation
	return map[string]interface{}{}, nil
}

func (s *AdminService) generateTimeBasedAnalysisReport(ctx context.Context, startDate, endDate time.Time) (map[string]interface{}, error) {
	// TODO: Implement actual time-based analysis
	return map[string]interface{}{}, nil
}

func (s *AdminService) generateTypeBasedAnalysisReport(ctx context.Context, startDate, endDate time.Time) (map[string]interface{}, error) {
	// TODO: Implement actual type-based analysis
	return map[string]interface{}{}, nil
}

func (s *AdminService) calculateKPIs(ctx context.Context) (map[string]float64, error) {
	// TODO: Implement actual KPI calculation
	// This would query flagged items and calculate:
	// - False Positive Rate
	// - False Negative Rate
	// - Accuracy
	// - Precision
	// - Recall
	// - F1 Score
	// - Throughput
	// - Average Review Time

	metrics := map[string]float64{
		domain.MetricFalsePositiveRate: 0.0,
		domain.MetricFalseNegativeRate: 0.0,
		domain.MetricAccuracy:          0.0,
		domain.MetricPrecision:         0.0,
		domain.MetricRecall:            0.0,
		domain.MetricF1Score:           0.0,
		domain.MetricThroughput:        0.0,
		domain.MetricAvgReviewTime:     0.0,
	}

	return metrics, nil
}

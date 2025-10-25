package handler

import (
	"net/http"
	"strconv"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"github.com/gin-gonic/gin"
)

var adminService *service.AdminService

// InitAdminHandler initializes the admin handler with dependencies
func InitAdminHandler(svc *service.AdminService, r *gin.Engine) {
	adminService = svc

	// Protected routes for admins only
	protected := r.Group("/api/admin")
	protected.Use(adminAuthMiddleware())
	{
		// Performance Reports
		protected.POST("/reports/generate", generateReportHandler)
		protected.GET("/reports", listReportsHandler)
		protected.GET("/reports/:id", getReportHandler)
		protected.GET("/reports/:id/download", downloadReportHandler)

		// KPI Monitoring
		protected.GET("/kpi/metrics", getKPIMetricsHandler)
		protected.GET("/kpi/history", getKPIHistoryHandler)
		protected.GET("/kpi/dashboard", getKPIDashboardHandler)

		// Auditor Performance Auditing
		protected.GET("/auditors/performance", getAllAuditorsPerformanceHandler)
		protected.GET("/auditors/:id/performance", getAuditorPerformanceHandler)
		protected.GET("/auditors/:id/reviews", getAuditorReviewsHandler)
		protected.GET("/auditors/efficiency", getAuditorsEfficiencyHandler)

		// Risk Threshold Management
		protected.GET("/config/risk-thresholds", getRiskThresholdsHandler)
		protected.PUT("/config/risk-thresholds", updateRiskThresholdsHandler)
		protected.GET("/config/risk-thresholds/history", getRiskThresholdsHistoryHandler)

		// System Configuration
		protected.GET("/config", getSystemConfigHandler)
		protected.PUT("/config/:key", updateSystemConfigHandler)
		protected.GET("/config/history", getSystemConfigHistoryHandler)

		// Case Assignment
		protected.POST("/cases/assign", assignCaseHandler)
		protected.POST("/cases/bulk-assign", bulkAssignCasesHandler)
		protected.GET("/cases/unassigned", getUnassignedCasesHandler)
		protected.GET("/cases/assignments", getCaseAssignmentsHandler)
		protected.PUT("/cases/assignments/:id", updateAssignmentHandler)
		protected.DELETE("/cases/assignments/:id", removeAssignmentHandler)
		protected.GET("/auditors/workload", getAuditorWorkloadHandler)

		// System Analytics
		protected.GET("/analytics/overview", getSystemOverviewHandler)
		protected.GET("/analytics/trends", getTrendAnalysisHandler)
		protected.GET("/analytics/throughput", getThroughputMetricsHandler)
	}
}

// Performance Reports Handlers

func generateReportHandler(c *gin.Context) {
	var req domain.GenerateReportRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get admin user ID from context
	adminID := c.GetString("user_id")
	if adminID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "admin not authenticated"})
		return
	}

	report, err := adminService.GeneratePerformanceReport(c.Request.Context(), req, adminID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"report": report})
}

func listReportsHandler(c *gin.Context) {
	limitStr := c.DefaultQuery("limit", "10")
	offsetStr := c.DefaultQuery("offset", "0")
	_ = c.Query("type")         // reportType - will be used when implemented
	_ = c.Query("generated_by") // generatedBy - will be used when implemented

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit <= 0 {
		limit = 10
	}

	offset, err := strconv.Atoi(offsetStr)
	if err != nil || offset < 0 {
		offset = 0
	}

	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{
		"reports": []domain.PerformanceReport{},
		"total":   0,
		"limit":   limit,
		"offset":  offset,
	})
}

func getReportHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// This would need to be implemented in the admin service
	// For now, return not found
	c.JSON(http.StatusNotFound, gin.H{"error": "report not found"})
}

func downloadReportHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// This would need to be implemented in the admin service
	// For now, return not found
	c.JSON(http.StatusNotFound, gin.H{"error": "report not found"})
}

// KPI Monitoring Handlers

func getKPIMetricsHandler(c *gin.Context) {
	metrics, err := adminService.GetKPIMetrics(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"metrics": metrics})
}

func getKPIHistoryHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"history": []domain.KPIMetrics{}})
}

func getKPIDashboardHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"dashboard": map[string]interface{}{}})
}

// Auditor Performance Handlers

func getAllAuditorsPerformanceHandler(c *gin.Context) {
	// Parse date range from query params
	startDateStr := c.Query("start_date")
	endDateStr := c.Query("end_date")

	// Default to last 30 days if not provided
	startDate := time.Now().AddDate(0, 0, -30)
	endDate := time.Now()

	if startDateStr != "" {
		if parsed, err := time.Parse("2006-01-02", startDateStr); err == nil {
			startDate = parsed
		}
	}
	if endDateStr != "" {
		if parsed, err := time.Parse("2006-01-02", endDateStr); err == nil {
			endDate = parsed
		}
	}

	reports, err := adminService.GetAllAuditorsPerformance(c.Request.Context(), startDate, endDate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"auditors_performance": reports})
}

func getAuditorPerformanceHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// Parse date range from query params
	startDateStr := c.Query("start_date")
	endDateStr := c.Query("end_date")

	// Default to last 30 days if not provided
	startDate := time.Now().AddDate(0, 0, -30)
	endDate := time.Now()

	if startDateStr != "" {
		if parsed, err := time.Parse("2006-01-02", startDateStr); err == nil {
			startDate = parsed
		}
	}
	if endDateStr != "" {
		if parsed, err := time.Parse("2006-01-02", endDateStr); err == nil {
			endDate = parsed
		}
	}

	report, err := adminService.GetAuditorPerformance(c.Request.Context(), id, startDate, endDate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"auditor_performance": report})
}

func getAuditorReviewsHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"reviews": []domain.FlaggedItem{}})
}

func getAuditorsEfficiencyHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"efficiency": []domain.AuditorPerformanceReport{}})
}

// Risk Threshold Management Handlers

func getRiskThresholdsHandler(c *gin.Context) {
	thresholds, err := adminService.GetRiskThresholds(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"risk_thresholds": thresholds})
}

func updateRiskThresholdsHandler(c *gin.Context) {
	var req domain.UpdateRiskThresholdRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get admin user ID from context
	adminID := c.GetString("user_id")
	if adminID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "admin not authenticated"})
		return
	}

	err := adminService.UpdateRiskThreshold(c.Request.Context(), req, adminID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Risk thresholds updated successfully"})
}

func getRiskThresholdsHistoryHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"history": []domain.SystemConfig{}})
}

// System Configuration Handlers

func getSystemConfigHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"config": []domain.SystemConfig{}})
}

func updateSystemConfigHandler(c *gin.Context) {
	key := c.Param("key")
	if key == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "key is required"})
		return
	}

	// This would need to be implemented in the admin service
	// For now, return not implemented
	c.JSON(http.StatusNotImplemented, gin.H{"error": "not implemented"})
}

func getSystemConfigHistoryHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"history": []domain.SystemConfig{}})
}

// Case Assignment Handlers

func assignCaseHandler(c *gin.Context) {
	var req domain.AssignCaseRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get admin user ID from context
	adminID := c.GetString("user_id")
	if adminID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "admin not authenticated"})
		return
	}

	assignment, err := adminService.AssignCase(c.Request.Context(), req, adminID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"assignment": assignment})
}

func bulkAssignCasesHandler(c *gin.Context) {
	var req domain.BulkAssignCasesRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get admin user ID from context
	adminID := c.GetString("user_id")
	if adminID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "admin not authenticated"})
		return
	}

	assignments, err := adminService.BulkAssignCases(c.Request.Context(), req, adminID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"assignments": assignments})
}

func getUnassignedCasesHandler(c *gin.Context) {
	limitStr := c.DefaultQuery("limit", "10")
	offsetStr := c.DefaultQuery("offset", "0")

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit <= 0 {
		limit = 10
	}

	offset, err := strconv.Atoi(offsetStr)
	if err != nil || offset < 0 {
		offset = 0
	}

	cases, total, err := adminService.GetUnassignedCases(c.Request.Context(), limit, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"cases":  cases,
		"total":  total,
		"limit":  limit,
		"offset": offset,
	})
}

func getCaseAssignmentsHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"assignments": []domain.CaseAssignment{}})
}

func updateAssignmentHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// This would need to be implemented in the admin service
	// For now, return not implemented
	c.JSON(http.StatusNotImplemented, gin.H{"error": "not implemented"})
}

func removeAssignmentHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// This would need to be implemented in the admin service
	// For now, return not implemented
	c.JSON(http.StatusNotImplemented, gin.H{"error": "not implemented"})
}

func getAuditorWorkloadHandler(c *gin.Context) {
	workload, err := adminService.GetAuditorWorkload(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"workload": workload})
}

// System Analytics Handlers

func getSystemOverviewHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"overview": map[string]interface{}{}})
}

func getTrendAnalysisHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"trends": map[string]interface{}{}})
}

func getThroughputMetricsHandler(c *gin.Context) {
	// This would need to be implemented in the admin service
	// For now, return empty response
	c.JSON(http.StatusOK, gin.H{"throughput": map[string]interface{}{}})
}

// adminAuthMiddleware is a placeholder for admin authentication middleware
func adminAuthMiddleware() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// TODO: Implement proper admin role authentication
		// For now, we'll use a placeholder admin ID
		c.Set("user_id", "admin-user-id")
		c.Next()
	})
}

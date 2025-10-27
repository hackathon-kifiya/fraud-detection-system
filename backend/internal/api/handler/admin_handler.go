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
	{

		// Auditor Performance Auditing
		protected.GET("/auditors/performance", getAllAuditorsPerformanceHandler)
		protected.GET("/auditors/:id/performance", getAuditorPerformanceHandler)

		// Case Assignment
		protected.POST("/cases/assign", assignCaseHandler)
		protected.POST("/cases/bulk-assign", bulkAssignCasesHandler)
		protected.GET("/cases/unassigned", getUnassignedCasesHandler)
		protected.GET("/cases/assignments", getCaseAssignmentsHandler)
		protected.PUT("/cases/assignments/:id", updateAssignmentHandler)
		protected.DELETE("/cases/assignments/:id", removeAssignmentHandler)
		protected.GET("/auditors/workload", getAuditorWorkloadHandler)

	}
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
	limitStr := c.DefaultQuery("limit", "10")
	offsetStr := c.DefaultQuery("offset", "0")
	status := c.Query("status")
	priority := c.Query("priority")

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit <= 0 {
		limit = 10
	}

	offset, err := strconv.Atoi(offsetStr)
	if err != nil || offset < 0 {
		offset = 0
	}

	assignments, total, err := adminService.GetCaseAssignments(c.Request.Context(), limit, offset, status, priority)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"assignments": assignments,
		"total":       total,
		"limit":       limit,
		"offset":      offset,
	})
}

func updateAssignmentHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	var req domain.UpdateAssignmentRequest
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

	assignment, err := adminService.UpdateCaseAssignment(c.Request.Context(), id, req, adminID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"assignment": assignment})
}

func removeAssignmentHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// Get admin user ID from context
	adminID := c.GetString("user_id")
	if adminID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "admin not authenticated"})
		return
	}

	err := adminService.RemoveCaseAssignment(c.Request.Context(), id, adminID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Assignment removed successfully"})
}

func getAuditorWorkloadHandler(c *gin.Context) {
	workload, err := adminService.GetAuditorWorkload(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"workload": workload})
}

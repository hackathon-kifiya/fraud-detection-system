package handler

import (
	"net/http"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"github.com/gin-gonic/gin"
)

var auditService *service.AuditService

// InitAuditHandler initializes the audit handler with dependencies
func InitAuditHandler(svc *service.AuditService, r *gin.Engine) {
	auditService = svc

	// Protected routes for auditors
	protected := r.Group("/api/audit")
	protected.Use(authMiddleware())
	{
		// List flagged items for review
		protected.GET("/flagged-items", listFlaggedItemsForReviewHandler)

		// Get detailed view of flagged item
		protected.GET("/flagged-items/:id/detail", getFlaggedItemDetailHandler)

		// Classify flagged item
		protected.POST("/flagged-items/:id/classify", classifyFlaggedItemHandler)

		// Add contextual note
		protected.POST("/flagged-items/:id/notes", addAuditNoteHandler)

		// Get all notes for flagged item
		protected.GET("/flagged-items/:id/notes", getAuditNotesHandler)

		// Get personal review history
		protected.GET("/my-reviews", getPersonalReviewHistoryHandler)

		// Get audit trail for flagged item
		protected.GET("/flagged-items/:id/audit-trail", getAuditTrailHandler)

		// Get auditor statistics
		protected.GET("/stats", getAuditStatsHandler)
	}
}

// listFlaggedItemsForReviewHandler handles listing flagged items for auditor review
func listFlaggedItemsForReviewHandler(c *gin.Context) {
	var req domain.FlaggedItemListRequest

	// Parse query parameters
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set defaults
	if req.Limit <= 0 {
		req.Limit = 10
	}
	if req.Offset < 0 {
		req.Offset = 0
	}

	response, err := auditService.ListFlaggedItemsForReview(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// getFlaggedItemDetailHandler handles getting detailed view of flagged item
func getFlaggedItemDetailHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	detail, err := auditService.GetFlaggedItemDetail(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"flagged_item_detail": detail})
}

// classifyFlaggedItemHandler handles classifying a flagged item
func classifyFlaggedItemHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	var req domain.ReviewClassificationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get user ID from context (assuming it's set by auth middleware)
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not authenticated"})
		return
	}

	err := auditService.ClassifyFlaggedItem(c.Request.Context(), id, req.Classification, userID, req.Notes)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Flagged item classified successfully"})
}

// addAuditNoteHandler handles adding a contextual note
func addAuditNoteHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	var req domain.AuditNoteRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get user ID from context
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not authenticated"})
		return
	}

	note, err := auditService.AddAuditNote(c.Request.Context(), id, userID, req.NoteText)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"audit_note": note})
}

// getAuditNotesHandler handles getting all notes for a flagged item
func getAuditNotesHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	// Get user ID from context
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not authenticated"})
		return
	}

	// Get notes using the audit service
	detail, err := auditService.GetFlaggedItemDetail(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"audit_notes": detail.AuditNotes})
}

// getPersonalReviewHistoryHandler handles getting personal review history
func getPersonalReviewHistoryHandler(c *gin.Context) {
	// Get user ID from context
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not authenticated"})
		return
	}

	var req domain.PersonalReviewHistoryRequest

	// Parse query parameters
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set defaults
	if req.Limit <= 0 {
		req.Limit = 10
	}
	if req.Offset < 0 {
		req.Offset = 0
	}

	response, err := auditService.GetPersonalReviewHistory(c.Request.Context(), userID, req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// getAuditTrailHandler handles getting audit trail for a flagged item
func getAuditTrailHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	trail, err := auditService.GetAuditTrail(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"audit_trail": trail})
}

// getAuditStatsHandler handles getting auditor statistics
func getAuditStatsHandler(c *gin.Context) {
	// Get user ID from context
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not authenticated"})
		return
	}

	stats, err := auditService.GetAuditStats(c.Request.Context(), userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"stats": stats})
}

package handler

import (
	"net/http"
	"strconv"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"github.com/gin-gonic/gin"
)

var flaggedItemService *service.FlaggedItemService

// InitFlaggedItemHandler initializes the flagged item handler with dependencies
func InitFlaggedItemHandler(svc *service.FlaggedItemService, r *gin.Engine) {
	flaggedItemService = svc

	// Public routes (for system to create flagged items)
	r.POST("/api/flagged-items", createFlaggedItemHandler)

	// Protected routes
	protected := r.Group("/api/flagged-items")
	protected.Use(authMiddleware())
	{
		protected.GET("", listFlaggedItemsHandler)
		protected.GET("/:id", getFlaggedItemHandler)
		protected.PUT("/:id", updateFlaggedItemHandler)
		protected.DELETE("/:id", deleteFlaggedItemHandler)
		protected.POST("/:id/verify", verifyFlaggedItemHandler)
		protected.GET("/stats", getStatsHandler)
		protected.GET("/type/:type", getFlaggedItemsByTypeHandler)
	}
}

// createFlaggedItemHandler handles creating a new flagged item
func createFlaggedItemHandler(c *gin.Context) {
	var req domain.CreateFlaggedItemRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	item, err := flaggedItemService.CreateFlaggedItem(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"flagged_item": item})
}

// listFlaggedItemsHandler handles listing flagged items
func listFlaggedItemsHandler(c *gin.Context) {
	limitStr := c.DefaultQuery("limit", "10")
	offsetStr := c.DefaultQuery("offset", "0")
	itemType := c.Query("type")
	status := c.Query("status")

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit <= 0 {
		limit = 10
	}

	offset, err := strconv.Atoi(offsetStr)
	if err != nil || offset < 0 {
		offset = 0
	}

	response, err := flaggedItemService.ListFlaggedItems(c.Request.Context(), limit, offset, itemType, status)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// getFlaggedItemHandler handles getting a flagged item by ID
func getFlaggedItemHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	item, err := flaggedItemService.GetFlaggedItem(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"flagged_item": item})
}

// updateFlaggedItemHandler handles updating a flagged item
func updateFlaggedItemHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	var req domain.UpdateFlaggedItemRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	item, err := flaggedItemService.UpdateFlaggedItem(c.Request.Context(), id, req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"flagged_item": item})
}

// deleteFlaggedItemHandler handles deleting a flagged item
func deleteFlaggedItemHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	err := flaggedItemService.DeleteFlaggedItem(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Flagged item deleted successfully"})
}

// verifyFlaggedItemHandler handles verifying a flagged item
func verifyFlaggedItemHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	var req struct {
		Status     string `json:"status" binding:"required"`
		ReviewedBy string `json:"reviewed_by" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	err := flaggedItemService.VerifyFlaggedItem(c.Request.Context(), id, req.Status, req.ReviewedBy)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Flagged item verified successfully"})
}

// getStatsHandler handles getting flagged item statistics
func getStatsHandler(c *gin.Context) {
	stats, err := flaggedItemService.GetStats(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"stats": stats})
}

// getFlaggedItemsByTypeHandler handles getting flagged items by type
func getFlaggedItemsByTypeHandler(c *gin.Context) {
	itemType := c.Param("type")
	if itemType == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "type is required"})
		return
	}

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

	response, err := flaggedItemService.GetFlaggedItemsByType(c.Request.Context(), itemType, limit, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

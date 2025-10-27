package handler

import (
	"net/http"
	"strconv"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"github.com/gin-gonic/gin"
)

var callbackService *service.CallbackService

// InitCallbackHandler initializes the callback handler with dependencies
func InitCallbackHandler(svc *service.CallbackService, r *gin.Engine) {
	callbackService = svc

	// Protected routes
	protected := r.Group("/api/callbacks")
	protected.Use(authMiddleware())
	{
		protected.GET("", listCallbacksHandler)
		protected.GET("/data-types/available", getAvailableDataTypesHandler)
		protected.GET("/:id", getCallbackHandler)
		protected.POST("", createCallbackHandler)
		protected.PUT("/:id", updateCallbackHandler)
		protected.DELETE("/:id", deleteCallbackHandler)
	}
}

// listCallbacksHandler lists all callbacks with pagination
func listCallbacksHandler(c *gin.Context) {
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
	offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))

	callbacks, total, err := callbackService.ListCallbacks(c.Request.Context(), limit, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to list callbacks"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"callbacks": callbacks,
		"total":     total,
		"limit":     limit,
		"offset":    offset,
	})
}

// getCallbackHandler retrieves a callback by ID
func getCallbackHandler(c *gin.Context) {
	id := c.Param("id")

	callback, err := callbackService.GetCallback(c.Request.Context(), id)
	if err != nil {
		if err == service.ErrCallbackNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "callback not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get callback"})
		return
	}

	c.JSON(http.StatusOK, callback)
}

// createCallbackHandler creates a new callback
func createCallbackHandler(c *gin.Context) {
	var req domain.CreateCallbackRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	callback, err := callbackService.CreateCallback(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create callback"})
		return
	}

	c.JSON(http.StatusCreated, callback)
}

// updateCallbackHandler updates a callback
func updateCallbackHandler(c *gin.Context) {
	id := c.Param("id")

	var req domain.UpdateCallbackRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	callback, err := callbackService.UpdateCallback(c.Request.Context(), id, req)
	if err != nil {
		if err == service.ErrCallbackNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "callback not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to update callback"})
		return
	}

	c.JSON(http.StatusOK, callback)
}

// deleteCallbackHandler deletes a callback
func deleteCallbackHandler(c *gin.Context) {
	id := c.Param("id")

	err := callbackService.DeleteCallback(c.Request.Context(), id)
	if err != nil {
		if err == service.ErrCallbackNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "callback not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to delete callback"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "callback deleted successfully"})
}

// getAvailableDataTypesHandler fetches available data types from data management service
func getAvailableDataTypesHandler(c *gin.Context) {
	dataTypes, err := callbackService.GetAvailableDataTypes()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch available data types"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data_types": dataTypes})
}

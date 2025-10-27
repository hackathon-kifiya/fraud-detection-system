package handler

import (
	"fmt"
	"net/http"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"github.com/gin-gonic/gin"
)

var evaluationService *service.EvaluationService

// InitEvaluationHandler initializes the evaluation handler
func InitEvaluationHandler(svc *service.EvaluationService, r *gin.Engine) {
	evaluationService = svc

	r.POST("/api/evaluate", evaluateHandler)
}

// evaluateHandler handles the evaluation endpoint
// This is a fire-and-forget endpoint - it returns immediately with acknowledgment
// The actual evaluation results are sent via callbacks asynchronously
func evaluateHandler(c *gin.Context) {
	var req domain.EvaluationRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	// Validate request
	if req.DataType == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "dataType is required",
		})
		return
	}

	if len(req.Facts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "facts array is required and cannot be empty",
		})
		return
	}

	// Process evaluation asynchronously - don't wait for results
	go func() {
		// This runs in the background
		result, err := evaluationService.Evaluate(c.Request.Context(), req)
		if err != nil {
			fmt.Printf("Evaluation failed: %v\n", err)
			return
		}
		// Result is handled by the service (callbacks or flagged items)
		fmt.Printf("Evaluation completed for entity %s with decision: %s\n", result.EntityID, result.Decision)
	}()

	// Return immediate acknowledgment - the actual results will be sent via callbacks
	c.JSON(http.StatusAccepted, gin.H{
		"success": true,
		"message": "Evaluation request accepted. Results will be sent via configured callbacks.",
	})
}

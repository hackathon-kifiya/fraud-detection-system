package handler

import (
	"net/http"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/client"
	"github.com/gin-gonic/gin"
)

var decisionServiceClient *client.DecisionServiceClient

// InitDecisionHandler initializes the decision handler with dependencies
func InitDecisionHandler(client *client.DecisionServiceClient, r *gin.Engine) {
	decisionServiceClient = client

	// Public routes (for making decisions)
	r.POST("/api/decide", makeDecisionHandler)
}

// makeDecisionHandler handles making a decision
func makeDecisionHandler(c *gin.Context) {
	var req client.DecisionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	decision, err := decisionServiceClient.MakeDecision(
		req.EntityID,
		req.RuleEngineScore,
		req.AnomalyDetectionScore,
		req.PredictiveEngineScore,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, decision)
}

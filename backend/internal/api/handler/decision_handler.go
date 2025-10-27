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

	// Data-type-specific configuration routes
	r.GET("/api/decision/config/data-types", getAllDataTypeConfigsHandler)
	r.GET("/api/decision/config/data-types/:dataType", getDataTypeConfigHandler)
	r.POST("/api/decision/config/data-types/:dataType", updateDataTypeConfigHandler)
	r.DELETE("/api/decision/config/data-types/:dataType", deleteDataTypeConfigHandler)
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
		req.DataType,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, decision)
}

// getAllDataTypeConfigsHandler handles getting all data types with custom configs
func getAllDataTypeConfigsHandler(c *gin.Context) {
	dataTypes, err := decisionServiceClient.GetAllDataTypeConfigs()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data_types": dataTypes})
}

// getDataTypeConfigHandler handles getting merged config for a specific data type
func getDataTypeConfigHandler(c *gin.Context) {
	dataType := c.Param("dataType")

	config, err := decisionServiceClient.GetDataTypeConfig(dataType)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, config)
}

// updateDataTypeConfigHandler handles updating data-type-specific config
func updateDataTypeConfigHandler(c *gin.Context) {
	dataType := c.Param("dataType")

	var req client.DataTypeDecisionConfig
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	req.DataType = dataType

	updatedConfig, err := decisionServiceClient.UpdateDataTypeConfig(dataType, req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, updatedConfig)
}

// deleteDataTypeConfigHandler handles deleting data-type-specific config
func deleteDataTypeConfigHandler(c *gin.Context) {
	dataType := c.Param("dataType")

	err := decisionServiceClient.DeleteDataTypeConfig(dataType)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Configuration for '" + dataType + "' reverted to defaults",
	})
}

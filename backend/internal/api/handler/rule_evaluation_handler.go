package handler

import (
	"net/http"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"github.com/gin-gonic/gin"
)

type RuleEvaluationHandler struct {
	ruleEvaluationService *service.RuleEvaluationService
}

// NewRuleEvaluationHandler creates a new rule evaluation handler
func NewRuleEvaluationHandler(ruleEvaluationService *service.RuleEvaluationService) *RuleEvaluationHandler {
	return &RuleEvaluationHandler{
		ruleEvaluationService: ruleEvaluationService,
	}
}

// EvaluateDataRequest represents the request to evaluate data
type EvaluateDataRequest struct {
	DataType string                   `json:"dataType" binding:"required"`
	Data     []map[string]interface{} `json:"data" binding:"required"`
}

// EvaluateDataResponse represents the response from data evaluation
type EvaluateDataResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
	Error   string `json:"error,omitempty"`
}

// EvaluateData evaluates data against rules
func (h *RuleEvaluationHandler) EvaluateData(c *gin.Context) {
	var req EvaluateDataRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, EvaluateDataResponse{
			Success: false,
			Error:   "Invalid request format: " + err.Error(),
		})
		return
	}

	err := h.ruleEvaluationService.EvaluateData(c.Request.Context(), req.DataType, req.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, EvaluateDataResponse{
			Success: false,
			Error:   "Failed to evaluate data: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, EvaluateDataResponse{
		Success: true,
		Message: "Data evaluated successfully",
	})
}

// EvaluateTransaction evaluates transaction data
func (h *RuleEvaluationHandler) EvaluateTransaction(c *gin.Context) {
	var req struct {
		Data []map[string]interface{} `json:"data" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, EvaluateDataResponse{
			Success: false,
			Error:   "Invalid request format: " + err.Error(),
		})
		return
	}

	err := h.ruleEvaluationService.EvaluateTransaction(c.Request.Context(), req.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, EvaluateDataResponse{
			Success: false,
			Error:   "Failed to evaluate transaction data: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, EvaluateDataResponse{
		Success: true,
		Message: "Transaction data evaluated successfully",
	})
}

// EvaluateKYC evaluates KYC data
func (h *RuleEvaluationHandler) EvaluateKYC(c *gin.Context) {
	var req struct {
		Data []map[string]interface{} `json:"data" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, EvaluateDataResponse{
			Success: false,
			Error:   "Invalid request format: " + err.Error(),
		})
		return
	}

	err := h.ruleEvaluationService.EvaluateKYC(c.Request.Context(), req.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, EvaluateDataResponse{
			Success: false,
			Error:   "Failed to evaluate KYC data: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, EvaluateDataResponse{
		Success: true,
		Message: "KYC data evaluated successfully",
	})
}

// EvaluateLoan evaluates loan data
func (h *RuleEvaluationHandler) EvaluateLoan(c *gin.Context) {
	var req struct {
		Data []map[string]interface{} `json:"data" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, EvaluateDataResponse{
			Success: false,
			Error:   "Invalid request format: " + err.Error(),
		})
		return
	}

	err := h.ruleEvaluationService.EvaluateLoan(c.Request.Context(), req.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, EvaluateDataResponse{
			Success: false,
			Error:   "Failed to evaluate loan data: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, EvaluateDataResponse{
		Success: true,
		Message: "Loan data evaluated successfully",
	})
}

// EvaluateCredit evaluates credit data
func (h *RuleEvaluationHandler) EvaluateCredit(c *gin.Context) {
	var req struct {
		Data []map[string]interface{} `json:"data" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, EvaluateDataResponse{
			Success: false,
			Error:   "Invalid request format: " + err.Error(),
		})
		return
	}

	err := h.ruleEvaluationService.EvaluateCredit(c.Request.Context(), req.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, EvaluateDataResponse{
			Success: false,
			Error:   "Failed to evaluate credit data: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, EvaluateDataResponse{
		Success: true,
		Message: "Credit data evaluated successfully",
	})
}

// EvaluateRepayment evaluates repayment data
func (h *RuleEvaluationHandler) EvaluateRepayment(c *gin.Context) {
	var req struct {
		Data []map[string]interface{} `json:"data" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, EvaluateDataResponse{
			Success: false,
			Error:   "Invalid request format: " + err.Error(),
		})
		return
	}

	err := h.ruleEvaluationService.EvaluateRepayment(c.Request.Context(), req.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, EvaluateDataResponse{
			Success: false,
			Error:   "Failed to evaluate repayment data: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, EvaluateDataResponse{
		Success: true,
		Message: "Repayment data evaluated successfully",
	})
}

// HealthCheck checks if the rule engine is healthy
func (h *RuleEvaluationHandler) HealthCheck(c *gin.Context) {
	err := h.ruleEvaluationService.HealthCheck()
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"status": "unhealthy",
			"error":  err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
	})
}

// CheckAllEnginesHealth handles health check requests for all engines
func (h *RuleEvaluationHandler) CheckAllEnginesHealth(c *gin.Context) {
	engines := make(map[string]interface{})

	// Check rule engine
	ruleEngineErr := h.ruleEvaluationService.HealthCheck()
	if ruleEngineErr != nil {
		engines["rule_engine"] = gin.H{"status": "down", "error": ruleEngineErr.Error()}
	} else {
		engines["rule_engine"] = gin.H{"status": "up"}
	}

	// Check other engines (these would need to be injected into the handler)
	// For now, we'll return a placeholder response
	engines["anomaly_detection_engine"] = gin.H{"status": "not_implemented", "message": "Client not yet integrated"}
	engines["predictive_engine"] = gin.H{"status": "not_implemented", "message": "Client not yet integrated"}
	engines["risk_aggregation_engine"] = gin.H{"status": "not_implemented", "message": "Client not yet integrated"}

	c.JSON(http.StatusOK, gin.H{
		"overall_status": "partial",
		"engines":        engines,
	})
}

// ValidateRule handles rule validation requests
func (h *RuleEvaluationHandler) ValidateRule(c *gin.Context) {
	var req struct {
		DrlContent string `json:"drlContent" binding:"required"`
		DataType   string `json:"dataType" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "Invalid request format: " + err.Error(),
		})
		return
	}

	// Call the rule engine validation service
	client := h.ruleEvaluationService.GetRuleEngineClient()
	response, err := client.ValidateRule(req.DrlContent, req.DataType)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   "Failed to validate rule: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":  true,
		"valid":    response.Valid,
		"errors":   response.Errors,
		"warnings": response.Warnings,
	})
}

// InitRuleEvaluationHandler initializes the rule evaluation handler
func InitRuleEvaluationHandler(ruleEvaluationService *service.RuleEvaluationService, r *gin.Engine) {
	handler := NewRuleEvaluationHandler(ruleEvaluationService)

	// API routes
	api := r.Group("/api/v1")
	{
		api.POST("/evaluate", handler.EvaluateData)
		api.POST("/evaluate/transaction", handler.EvaluateTransaction)
		api.POST("/evaluate/kyc", handler.EvaluateKYC)
		api.POST("/evaluate/loan", handler.EvaluateLoan)
		api.POST("/evaluate/credit", handler.EvaluateCredit)
		api.POST("/evaluate/repayment", handler.EvaluateRepayment)
		api.GET("/rule-engine/health", handler.HealthCheck)
		api.GET("/engines/health", handler.CheckAllEnginesHealth)
		api.POST("/validate-rule", handler.ValidateRule)
	}
}

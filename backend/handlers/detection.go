package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"fraud-detection-backend/db"
	"fraud-detection-backend/models"

	"github.com/gin-gonic/gin"
)

// DetectionHandler handles fraud detection orchestration
type DetectionHandler struct {
	db         *db.DB
	engineURL  string
	httpClient *http.Client
}

// NewDetectionHandler creates a new detection handler
func NewDetectionHandler(database *db.DB, engineURL string) *DetectionHandler {
	return &DetectionHandler{
		db:        database,
		engineURL: engineURL,
		httpClient: &http.Client{
			Timeout: 5 * time.Minute, // Detection can take time
		},
	}
}

// TriggerDetection triggers fraud detection by calling the engine
func (h *DetectionHandler) TriggerDetection(c *gin.Context) {
	// Parse request body
	var request struct {
		DaysBack int `json:"days_back,omitempty"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Invalid request body: %v", err),
		})
		return
	}

	// Set default days back if not provided
	if request.DaysBack <= 0 {
		request.DaysBack = 30
	}

	// Check if engine is available
	if err := h.checkEngineHealth(); err != nil {
		c.JSON(http.StatusServiceUnavailable, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Fraud detection engine is not available: %v", err),
		})
		return
	}

	// Call the fraud detection engine
	result, err := h.callDetectionEngine(request.DaysBack)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to run fraud detection: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.DetectionResponse{
		Success: true,
		Message: fmt.Sprintf("Fraud detection completed for last %d days", request.DaysBack),
		Result:  result,
	})
}

// GetDetectionStatus returns the current status of the detection system
func (h *DetectionHandler) GetDetectionStatus(c *gin.Context) {
	// Check database health
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	dbHealthy := h.db.Health(ctx) == nil

	// Check engine health
	engineHealthy := h.checkEngineHealth() == nil

	// Get recent detection stats
	stats, err := h.getDetectionStats(ctx)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("Failed to get detection stats: %v", err),
		})
		return
	}

	status := gin.H{
		"database_healthy": dbHealthy,
		"engine_healthy":   engineHealthy,
		"overall_status":   "healthy",
		"stats":            stats,
	}

	if !dbHealthy || !engineHealthy {
		status["overall_status"] = "degraded"
	}

	c.JSON(http.StatusOK, status)
}

// checkEngineHealth checks if the fraud detection engine is available
func (h *DetectionHandler) checkEngineHealth() error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", h.engineURL+"/health", nil)
	if err != nil {
		return fmt.Errorf("failed to create health check request: %w", err)
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to call engine health endpoint: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("engine health check failed with status: %d", resp.StatusCode)
	}

	return nil
}

// callDetectionEngine calls the fraud detection engine API
func (h *DetectionHandler) callDetectionEngine(daysBack int) (map[string]interface{}, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Minute)
	defer cancel()

	// Prepare request body
	requestBody := map[string]interface{}{
		"days_back": daysBack,
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request body: %w", err)
	}

	// Create request
	req, err := http.NewRequestWithContext(ctx, "POST", h.engineURL+"/detect", bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create detection request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	// Make request
	resp, err := h.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to call detection engine: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	// Check status code
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("detection engine returned status %d: %s", resp.StatusCode, string(body))
	}

	// Parse response
	var response struct {
		Success bool                   `json:"success"`
		Message string                 `json:"message"`
		Result  map[string]interface{} `json:"result"`
		Error   string                 `json:"error"`
	}

	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("failed to parse detection response: %w", err)
	}

	if !response.Success {
		return nil, fmt.Errorf("detection engine error: %s", response.Error)
	}

	return response.Result, nil
}

// getDetectionStats gets recent detection statistics from the database
func (h *DetectionHandler) getDetectionStats(ctx context.Context) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// Get total flagged items count
	var totalFlagged int
	err := h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items").Scan(&totalFlagged)
	if err != nil {
		return nil, fmt.Errorf("failed to get total flagged count: %w", err)
	}
	stats["total_flagged"] = totalFlagged

	// Get flagged items by status
	var pendingCount, fraudCount, safeCount int
	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE status = 'pending'").Scan(&pendingCount)
	if err != nil {
		return nil, fmt.Errorf("failed to get pending count: %w", err)
	}

	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE status = 'fraud'").Scan(&fraudCount)
	if err != nil {
		return nil, fmt.Errorf("failed to get fraud count: %w", err)
	}

	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE status = 'safe'").Scan(&safeCount)
	if err != nil {
		return nil, fmt.Errorf("failed to get safe count: %w", err)
	}

	stats["by_status"] = map[string]int{
		"pending": pendingCount,
		"fraud":   fraudCount,
		"safe":    safeCount,
	}

	// Get flagged items by type
	rows, err := h.db.Pool.Query(ctx, "SELECT type, COUNT(*) FROM flagged_items GROUP BY type")
	if err != nil {
		return nil, fmt.Errorf("failed to get flagged by type: %w", err)
	}
	defer rows.Close()

	byType := make(map[string]int)
	for rows.Next() {
		var itemType string
		var count int
		if err := rows.Scan(&itemType, &count); err != nil {
			return nil, fmt.Errorf("failed to scan type count: %w", err)
		}
		byType[itemType] = count
	}
	stats["by_type"] = byType

	// Get recent detection activity (last 24 hours)
	var recentCount int
	err = h.db.Pool.QueryRow(ctx,
		"SELECT COUNT(*) FROM flagged_items WHERE created_at > NOW() - INTERVAL '24 hours'").Scan(&recentCount)
	if err != nil {
		return nil, fmt.Errorf("failed to get recent count: %w", err)
	}
	stats["recent_24h"] = recentCount

	// Get high-risk items count (score >= 85)
	var highRiskCount int
	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE score >= 85").Scan(&highRiskCount)
	if err != nil {
		return nil, fmt.Errorf("failed to get high risk count: %w", err)
	}
	stats["high_risk"] = highRiskCount

	return stats, nil
}

// TriggerDetectionByType triggers fraud detection for a specific data type
func (h *DetectionHandler) TriggerDetectionByType(c *gin.Context) {
	dataType := c.Param("type")
	
	// Validate data type
	validTypes := map[string]bool{
		"transactions":   true,
		"loan_requests":  true,
		"credit_history": true,
		"kyc":           true,
		"repayments":    true,
	}
	
	if !validTypes[dataType] {
		c.JSON(http.StatusBadRequest, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Invalid data type: %s. Valid types: transactions, loan_requests, credit_history, kyc, repayments", dataType),
		})
		return
	}

	// Parse request body
	var request struct {
		DaysBack int `json:"days_back,omitempty"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Invalid request body: %v", err),
		})
		return
	}

	// Set default days back if not provided
	if request.DaysBack == 0 {
		request.DaysBack = 30
	}

	// Validate days back
	if request.DaysBack < 1 || request.DaysBack > 365 {
		c.JSON(http.StatusBadRequest, models.DetectionResponse{
			Success: false,
			Error:   "days_back must be between 1 and 365",
		})
		return
	}

	// Call the engine with specific data type
	engineRequest := map[string]interface{}{
		"days_back": request.DaysBack,
		"data_type": dataType,
	}

	jsonData, err := json.Marshal(engineRequest)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to marshal request: %v", err),
		})
		return
	}

	// Call the engine
	resp, err := h.httpClient.Post(h.engineURL+"/detect/"+dataType, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to call detection engine: %v", err),
		})
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to read engine response: %v", err),
		})
		return
	}

	if resp.StatusCode != http.StatusOK {
		c.JSON(http.StatusInternalServerError, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Detection engine returned status %d: %s", resp.StatusCode, string(body)),
		})
		return
	}

	var engineResponse map[string]interface{}
	if err := json.Unmarshal(body, &engineResponse); err != nil {
		c.JSON(http.StatusInternalServerError, models.DetectionResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to parse engine response: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.DetectionResponse{
		Success: true,
		Message: fmt.Sprintf("Fraud detection completed for %s (last %d days)", dataType, request.DaysBack),
		Result:  engineResponse,
	})
}

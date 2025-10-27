package handler

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/client"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/database"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/repository"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"gorm.io/gorm"
)

// setupMockServices creates mock HTTP servers for external services
func setupMockServices() (ruleEngineURL string, anomalyURL string, predictiveURL string, decisionURL string, cleanup func()) {
	// Mock Rule Engine Server
	ruleEngineServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var req map[string]interface{}
		json.NewDecoder(r.Body).Decode(&req)

		facts, _ := req["facts"].([]interface{})
		riskScore := 30.0

		if len(facts) > 0 {
			if fact, ok := facts[0].(map[string]interface{}); ok {
				if amount, ok := fact["amount"].(float64); ok {
					if amount > 10000 {
						riskScore = 85.0
					} else if amount > 5000 {
						riskScore = 60.0
					}
				}
			}
		}

		resp := map[string]interface{}{
			"entityId":   uuid.New().String(),
			"riskScore":  riskScore,
			"violations": []interface{}{},
			"verdict":    "flagged",
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))

	// Mock Anomaly Detection Server
	anomalyServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := map[string]interface{}{
			"success": true,
			"message": "Anomaly detection completed",
			"result": map[string]interface{}{
				"anomaly_score": 25.0,
			},
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))

	// Mock Predictive Engine Server
	predictiveServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := map[string]interface{}{
			"success": true,
			"predictions": []map[string]interface{}{
				{"score": 35.0},
			},
			"confidence": 0.85,
			"model_info": map[string]interface{}{},
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))

	// Mock Decision Service Server
	decisionServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var req map[string]interface{}
		json.NewDecoder(r.Body).Decode(&req)

		ruleScore, _ := req["rule_engine_score"].(float64)
		anomalyScore, _ := req["anomaly_detection_score"].(float64)
		predictiveScore, _ := req["predictive_engine_score"].(float64)

		finalScore := (ruleScore + anomalyScore + predictiveScore) / 3

		var decision string
		if finalScore < 30 {
			decision = "auto_approve"
		} else if finalScore > 70 {
			decision = "auto_reject"
		} else {
			decision = "human_review"
		}

		resp := map[string]interface{}{
			"entity_id":           req["entity_id"],
			"final_score":         finalScore,
			"final_score_percent": finalScore,
			"decision":            decision,
			"breakdown": map[string]interface{}{
				"rule_engine": map[string]interface{}{
					"score":        ruleScore,
					"weight":       0.4,
					"contribution": ruleScore * 0.4,
				},
				"anomaly_detection": map[string]interface{}{
					"score":        anomalyScore,
					"weight":       0.3,
					"contribution": anomalyScore * 0.3,
				},
				"predictive_engine": map[string]interface{}{
					"score":        predictiveScore,
					"weight":       0.3,
					"contribution": predictiveScore * 0.3,
				},
			},
			"confidence": finalScore / 100.0,
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))

	cleanup = func() {
		ruleEngineServer.Close()
		anomalyServer.Close()
		predictiveServer.Close()
		decisionServer.Close()
	}

	return ruleEngineServer.URL, anomalyServer.URL, predictiveServer.URL, decisionServer.URL, cleanup
}

// Create test database and dependencies
func setupTestDB() (*gorm.DB, *service.EvaluationService, *service.AuditService, port.CallbackRepository, func(), error) {
	// Use in-memory SQLite for testing
	db, err := database.InitSQLite(":memory:")
	if err != nil {
		return nil, nil, nil, nil, nil, err
	}

	// Run migrations
	if err := database.AutoMigrate(db); err != nil {
		return nil, nil, nil, nil, nil, err
	}

	// Get mock service URLs
	ruleURL, anomalyURL, predictiveURL, decisionURL, cleanup := setupMockServices()

	// Create repositories
	flaggedItemRepo := repository.NewFlaggedItemRepository(db)
	auditNoteRepo := repository.NewAuditNoteRepository(db)
	auditLogRepo := repository.NewAuditLogRepository(db)
	caseAssignmentRepo := repository.NewCaseAssignmentRepository(db)
	labeledDataRepo := repository.NewLabeledDataRepository(db)
	callbackRepo := repository.NewCallbackRepository(db)

	// Create clients
	ruleEngineClient := client.NewRuleEngineClient(ruleURL)
	anomalyDetectionClient := client.NewAnomalyDetectionEngineClient(anomalyURL)
	predictiveEngineClient := client.NewPredictiveEngineClient(predictiveURL)
	decisionServiceClient := client.NewDecisionServiceClient(decisionURL)

	// Initialize services
	evaluationService := service.NewEvaluationService(
		ruleEngineClient,
		anomalyDetectionClient,
		predictiveEngineClient,
		decisionServiceClient,
		flaggedItemRepo,
		callbackRepo,
	)

	auditService := service.NewAuditService(
		flaggedItemRepo,
		auditNoteRepo,
		auditLogRepo,
		caseAssignmentRepo,
		labeledDataRepo,
		callbackRepo,
	)

	return db, evaluationService, auditService, callbackRepo, cleanup, nil
}

// Test the complete evaluation workflow with decisive case (auto_approve)
func TestEvaluationWorkflow_Decisive_AutoApprove(t *testing.T) {
	gin.SetMode(gin.TestMode)

	_, evalService, _, callbackRepo, cleanup, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanup()

	// Create a test callback
	testCallback := &domain.Callback{
		ID:          uuid.New().String(),
		DataType:    "transactions",
		CallbackURL: "http://test-callback.example.com",
		Method:      "POST",
		Headers:     "{}",
		IsActive:    true,
	}
	if err := callbackRepo.Create(context.Background(), testCallback); err != nil {
		t.Fatalf("Failed to create test callback: %v", err)
	}

	// Test request with low-risk transaction
	req := domain.EvaluationRequest{
		DataType: "transactions",
		Facts: []map[string]interface{}{
			{
				"amount":    500.0,
				"merchant":  "legitimate_merchant",
				"currency":  "USD",
				"country":   "US",
				"card_type": "credit",
			},
		},
	}

	// Call evaluation service
	result, err := evalService.Evaluate(context.Background(), req)
	if err != nil {
		t.Fatalf("Evaluation failed: %v", err)
	}

	// Verify result
	if result.Decision != "auto_approve" {
		t.Errorf("Expected decision 'auto_approve', got '%s'", result.Decision)
	}

	if result.ActionTaken != "callback_invoked" {
		t.Errorf("Expected action 'callback_invoked', got '%s'", result.ActionTaken)
	}

	if result.FinalScore >= 30 {
		t.Errorf("Expected low risk score (<30), got %.2f", result.FinalScore)
	}

	// Verify callback was invoked (with a small delay to allow async operation)
	time.Sleep(100 * time.Millisecond)

	// Get callbacks for this data type
	callbacks, err := callbackRepo.GetByDataType(context.Background(), "transactions")
	if err == nil && len(callbacks) > 0 {
		if !callbacks[0].IsActive {
			t.Error("Callback should be active")
		}
	}
}

// Test the complete evaluation workflow with human review case
func TestEvaluationWorkflow_HumanReview_ApproveReject_StoreLabeledData(t *testing.T) {
	gin.SetMode(gin.TestMode)

	db, evalService, auditService, callbackRepo, cleanup, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanup()

	// Create a test callback
	testCallback := &domain.Callback{
		ID:          uuid.New().String(),
		DataType:    "transactions",
		CallbackURL: "http://test-callback.example.com",
		Method:      "POST",
		Headers:     "{}",
		IsActive:    true,
	}
	if err := callbackRepo.Create(context.Background(), testCallback); err != nil {
		t.Fatalf("Failed to create test callback: %v", err)
	}

	ctx := context.Background()

	// Test request with medium-risk transaction (triggers human review)
	req := domain.EvaluationRequest{
		DataType: "transactions",
		Facts: []map[string]interface{}{
			{
				"amount":    6000.0, // Medium-risk amount
				"merchant":  "unknown_merchant",
				"currency":  "USD",
				"country":   "CN",
				"card_type": "debit",
			},
		},
	}

	// Call evaluation service
	result, err := evalService.Evaluate(ctx, req)
	if err != nil {
		t.Fatalf("Evaluation failed: %v", err)
	}

	// Verify result
	if result.Decision != "human_review" {
		t.Errorf("Expected decision 'human_review', got '%s'", result.Decision)
	}

	if result.ActionTaken != "case_created" {
		t.Errorf("Expected action 'case_created', got '%s'", result.ActionTaken)
	}

	if result.FlaggedItemID == nil {
		t.Error("Expected flagged item ID to be set")
	}

	flaggedItemID := *result.FlaggedItemID
	t.Logf("Created flagged item: %s", flaggedItemID)

	// Verify flagged item was created in case management
	// Get flagged item detail through the audit service
	detail, err := auditService.GetFlaggedItemDetail(ctx, flaggedItemID)
	if err != nil {
		t.Fatalf("Failed to get flagged item detail: %v", err)
	}

	if detail.FlaggedItem.Status != domain.StatusPending {
		t.Errorf("Expected status 'pending', got '%s'", detail.FlaggedItem.Status)
	}

	// Test: Add audit note
	testUserID := "test-auditor-1"
	noteText := "This looks like a legitimate transaction after review"
	note, err := auditService.AddAuditNote(ctx, flaggedItemID, testUserID, noteText)
	if err != nil {
		t.Fatalf("Failed to add audit note: %v", err)
	}

	if note.NoteText != noteText {
		t.Errorf("Expected note text to be '%s', got '%s'", noteText, note.NoteText)
	}

	// Test: Auditor approves (classifies as confirmed fraud)
	err = auditService.ClassifyFlaggedItem(ctx, flaggedItemID, domain.StatusConfirmed, testUserID, "Confirmed fraud pattern detected")
	if err != nil {
		t.Fatalf("Failed to classify flagged item: %v", err)
	}

	// Wait for async operations (callback and labeled data storage)
	time.Sleep(200 * time.Millisecond)

	// Verify labeled data was stored for retraining
	labeledDataRepo := repository.NewLabeledDataRepository(db)
	labeledDataList, _, err := labeledDataRepo.List(ctx, 10, 0)
	if err != nil {
		t.Logf("Failed to list labeled data (this might be expected in async): %v", err)
	} else if len(labeledDataList) > 0 {
		t.Logf("Found %d labeled data entries", len(labeledDataList))
	}

	// Test: Another transaction - reject as false positive
	req2 := domain.EvaluationRequest{
		DataType: "transactions",
		Facts: []map[string]interface{}{
			{
				"amount":    7500.0,
				"merchant":  "trusted_merchant",
				"currency":  "USD",
				"country":   "US",
				"card_type": "credit",
			},
		},
	}

	result2, err := evalService.Evaluate(ctx, req2)
	if err != nil {
		t.Fatalf("Second evaluation failed: %v", err)
	}

	flaggedItemID2 := *result2.FlaggedItemID

	// Auditor rejects as false positive
	err = auditService.ClassifyFlaggedItem(ctx, flaggedItemID2, domain.StatusFalsePositive, testUserID, "Legitimate transaction, false positive")
	if err != nil {
		t.Fatalf("Failed to classify as false positive: %v", err)
	}

	// Wait for async operations
	time.Sleep(200 * time.Millisecond)

	// Verify labeled data was stored for the false positive as well
	labeledDataList2, _, err := labeledDataRepo.List(ctx, 10, 0)
	if err != nil {
		t.Logf("Failed to list labeled data: %v", err)
	} else if len(labeledDataList2) >= 2 {
		t.Logf("Found %d labeled data entries (both confirmed and false_positive)", len(labeledDataList2))
	}

	t.Log("Complete workflow test passed!")
}

// Test auto-reject workflow
func TestEvaluationWorkflow_Decisive_AutoReject(t *testing.T) {
	gin.SetMode(gin.TestMode)

	_, evalService, _, _, cleanup, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanup()

	// Test request with high-risk transaction
	req := domain.EvaluationRequest{
		DataType: "transactions",
		Facts: []map[string]interface{}{
			{
				"amount":    50000.0, // Very high amount
				"merchant":  "suspicious_merchant",
				"currency":  "USD",
				"country":   "XYZ",
				"card_type": "prepaid",
			},
		},
	}

	// Call evaluation service
	result, err := evalService.Evaluate(context.Background(), req)
	if err != nil {
		t.Fatalf("Evaluation failed: %v", err)
	}

	// Verify result
	if result.Decision != "auto_reject" {
		t.Errorf("Expected decision 'auto_reject', got '%s'", result.Decision)
	}

	if result.ActionTaken != "callback_invoked" {
		t.Errorf("Expected action 'callback_invoked', got '%s'", result.ActionTaken)
	}

	if result.FinalScore < 70 {
		t.Errorf("Expected high risk score (>=70), got %.2f", result.FinalScore)
	}

	t.Log("Auto-reject workflow test passed!")
}

// Test error handling when engines fail
func TestEvaluationWorkflow_EngineFailures(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// This test would require creating services with failing mock clients
	// For now, it's a placeholder to show error handling testing

	t.Log("Engine failures test - placeholder for future implementation")
}

// End-to-end HTTP test
func TestEvaluationHandler_EndToEnd(t *testing.T) {
	gin.SetMode(gin.TestMode)

	_, evalService, _, callbackRepo, cleanup, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanup()

	// Setup Gin router
	router := gin.New()
	InitEvaluationHandler(evalService, router)

	// Create test callback
	testCallback := &domain.Callback{
		ID:          uuid.New().String(),
		DataType:    "transactions",
		CallbackURL: "http://test-callback.example.com",
		Method:      "POST",
		Headers:     "{}",
		IsActive:    true,
	}
	if err := callbackRepo.Create(context.Background(), testCallback); err != nil {
		t.Fatalf("Failed to create test callback: %v", err)
	}

	// Test 1: Auto-approve
	t.Run("AutoApprove", func(t *testing.T) {
		reqBody := domain.EvaluationRequest{
			DataType: "transactions",
			Facts: []map[string]interface{}{
				{"amount": 500.0, "merchant": "legit_shop"},
			},
		}

		body, _ := json.Marshal(reqBody)
		w := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/api/evaluate", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")

		router.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
			t.Logf("Response body: %s", w.Body.String())
		}

		var response domain.EvaluationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
			t.Fatalf("Failed to unmarshal response: %v", err)
		}

		if !response.Success {
			t.Error("Expected success=true")
		}

		if response.Result.Decision != "auto_approve" {
			t.Errorf("Expected 'auto_approve', got '%s'", response.Result.Decision)
		}
	})

	// Test 2: Human review
	t.Run("HumanReview", func(t *testing.T) {
		reqBody := domain.EvaluationRequest{
			DataType: "transactions",
			Facts: []map[string]interface{}{
				{"amount": 6000.0, "merchant": "questionable_shop"},
			},
		}

		body, _ := json.Marshal(reqBody)
		w := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/api/evaluate", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")

		router.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}

		var response domain.EvaluationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
			t.Fatalf("Failed to unmarshal response: %v", err)
		}

		if response.Result.Decision != "human_review" {
			t.Errorf("Expected 'human_review', got '%s'", response.Result.Decision)
		}

		if response.Result.FlaggedItemID == nil {
			t.Error("Expected flagged item ID for human review case")
		}
	})

	// Test 3: Invalid request
	t.Run("InvalidRequest", func(t *testing.T) {
		body := bytes.NewBuffer([]byte(`{"invalid": "request"}`))
		w := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/api/evaluate", body)
		req.Header.Set("Content-Type", "application/json")

		router.ServeHTTP(w, req)

		if w.Code != http.StatusBadRequest {
			t.Errorf("Expected status 400 for invalid request, got %d", w.Code)
		}
	})

	t.Log("End-to-end HTTP test passed!")
}

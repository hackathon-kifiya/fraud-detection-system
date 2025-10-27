package service

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/client"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"github.com/google/uuid"
)

type EvaluationService struct {
	ruleEngineClient       *client.RuleEngineClient
	anomalyDetectionClient *client.AnomalyDetectionEngineClient
	predictiveEngineClient *client.PredictiveEngineClient
	decisionServiceClient  *client.DecisionServiceClient
	flaggedItemRepo        port.FlaggedItemRepository
	callbackRepo           port.CallbackRepository
}

func NewEvaluationService(
	ruleEngineClient *client.RuleEngineClient,
	anomalyDetectionClient *client.AnomalyDetectionEngineClient,
	predictiveEngineClient *client.PredictiveEngineClient,
	decisionServiceClient *client.DecisionServiceClient,
	flaggedItemRepo port.FlaggedItemRepository,
	callbackRepo port.CallbackRepository,
) *EvaluationService {
	return &EvaluationService{
		ruleEngineClient:       ruleEngineClient,
		anomalyDetectionClient: anomalyDetectionClient,
		predictiveEngineClient: predictiveEngineClient,
		decisionServiceClient:  decisionServiceClient,
		flaggedItemRepo:        flaggedItemRepo,
		callbackRepo:           callbackRepo,
	}
}

// Evaluate orchestrates the evaluation workflow across all engines
func (s *EvaluationService) Evaluate(ctx context.Context, req domain.EvaluationRequest) (*domain.EvaluationResult, error) {
	// Generate entity ID
	entityID := uuid.New().String()

	// Collect errors from engines
	errors := make(map[string]string)

	// 1. Call Rule Engine
	ruleEngineScore := 0.0
	ruleEngineResp, err := s.ruleEngineClient.Evaluate(req.DataType, req.Facts)
	if err != nil {
		errors["rule_engine"] = err.Error()
		fmt.Printf("Warning: rule engine failed: %v\n", err)
	} else {
		ruleEngineScore = ruleEngineResp.RiskScore
	}

	// 2. Call Anomaly Detection Engine
	anomalyScore := 0.0
	anomalyResp, err := s.anomalyDetectionClient.DetectAnomalies(7, req.Facts)
	if err != nil {
		errors["anomaly_detection"] = err.Error()
		fmt.Printf("Warning: anomaly detection engine failed: %v\n", err)
	} else {
		// Extract score from response
		if anomalyResp.Result != nil {
			if score, ok := anomalyResp.Result["anomaly_score"].(float64); ok {
				anomalyScore = score
			}
		}
	}

	// 3. Call Decision Service (predictive engine removed - using 0.0 as placeholder)
	predictiveScore := 0.0
	decisionResp, err := s.decisionServiceClient.MakeDecision(entityID, ruleEngineScore, anomalyScore, predictiveScore, req.DataType)
	if err != nil {
		errors["decision_service"] = err.Error()
		fmt.Printf("Warning: decision service failed: %v\n", err)

		// Default to human review if decision service fails (using 2 engines)
		avgScore := (ruleEngineScore + anomalyScore) / 2
		finalScorePercent := avgScore * 100
		decisionResp = &client.DecisionResponse{
			EntityID:          entityID,
			FinalScore:        avgScore,
			FinalScorePercent: finalScorePercent,
			Decision:          "human_review",
			Confidence:        0.5,
			Breakdown: client.ScoreBreakdown{
				RuleEngine: struct {
					Score        float64 `json:"score"`
					Weight       float64 `json:"weight"`
					Contribution float64 `json:"contribution"`
				}{
					Score:        ruleEngineScore,
					Weight:       50.0,
					Contribution: ruleEngineScore * 0.5,
				},
				AnomalyDetection: struct {
					Score        float64 `json:"score"`
					Weight       float64 `json:"weight"`
					Contribution float64 `json:"contribution"`
				}{
					Score:        anomalyScore,
					Weight:       50.0,
					Contribution: anomalyScore * 0.5,
				},
				PredictiveEngine: struct {
					Score        float64 `json:"score"`
					Weight       float64 `json:"weight"`
					Contribution float64 `json:"contribution"`
				}{
					Score:        0.0,
					Weight:       0.0,
					Contribution: 0.0,
				},
			},
		}
	}

	// 5. Route based on decision
	actionTaken := ""
	flaggedItemID := (*string)(nil)

	fmt.Printf("DEBUG: decisionResp.Decision value: '%s'\n", decisionResp.Decision)

	// Always invoke callbacks with the evaluation results
	// Callbacks are the primary way results are returned to clients
	s.invokeCallbackAsync(ctx, req.DataType, entityID, decisionResp, req.Facts)

	switch decisionResp.Decision {
	case "auto_approve", "auto_reject":
		actionTaken = "callback_invoked"
		// Results sent via callback above

	case "HUMAN_REVIEW", "human_review":
		actionTaken = "case_created"
		fmt.Printf("Creating flagged item with decisionResp: Decision=%s, FinalScorePercent=%f, Confidence=%f\n",
			decisionResp.Decision, decisionResp.FinalScorePercent, decisionResp.Confidence)
		fmt.Printf("Breakdown: %+v\n", decisionResp.Breakdown)

		// Create decision breakdown JSON
		breakdownJSON, err := json.Marshal(decisionResp.Breakdown)
		if err != nil {
			fmt.Printf("Warning: failed to marshal breakdown: %v\n", err)
		} else {
			fmt.Printf("Decision Breakdown JSON: %s\n", string(breakdownJSON))
		}

		// Create flagged item for human review
		finalScorePercent := decisionResp.FinalScorePercent
		confidence := decisionResp.Confidence
		fmt.Printf("Storing - FinalScorePercent: %f, Confidence: %f, Breakdown length: %d\n",
			finalScorePercent, confidence, len(breakdownJSON))
		flaggedItem := &domain.FlaggedItem{
			Type:              req.DataType,
			DataID:            entityID,
			Reason:            "Multi-engine evaluation flagged for review",
			RiskScore:         decisionResp.FinalScore,
			Status:            domain.StatusPending,
			Details:           fmt.Sprintf(`{"rule_engine_score": %f, "anomaly_score": %f}`, ruleEngineScore, anomalyScore),
			RuleEngineScore:   &ruleEngineScore,
			AnomalyScore:      &anomalyScore,
			MLScore:           nil,
			DecisionBreakdown: string(breakdownJSON),
			Confidence:        &confidence,
			FinalScorePercent: &finalScorePercent,
			FlaggedBy:         "system",
		}

		if err := s.flaggedItemRepo.Create(ctx, flaggedItem); err != nil {
			fmt.Printf("Warning: failed to create flagged item: %v\n", err)
		} else {
			flaggedItemID = &flaggedItem.ID
		}
		// Callback already invoked above
	}

	// Build breakdown
	breakdown := map[string]interface{}{
		"rule_engine": map[string]interface{}{
			"score": ruleEngineScore,
		},
		"anomaly_detection": map[string]interface{}{
			"score": anomalyScore,
		},
		"predictive_engine": map[string]interface{}{
			"score": 0.0,
		},
	}

	if decisionResp.Breakdown.RuleEngine.Weight > 0 {
		breakdown["rule_engine"] = map[string]interface{}{
			"score":        decisionResp.Breakdown.RuleEngine.Score,
			"weight":       decisionResp.Breakdown.RuleEngine.Weight,
			"contribution": decisionResp.Breakdown.RuleEngine.Contribution,
		}
		breakdown["anomaly_detection"] = map[string]interface{}{
			"score":        decisionResp.Breakdown.AnomalyDetection.Score,
			"weight":       decisionResp.Breakdown.AnomalyDetection.Weight,
			"contribution": decisionResp.Breakdown.AnomalyDetection.Contribution,
		}
		breakdown["predictive_engine"] = map[string]interface{}{
			"score":        decisionResp.Breakdown.PredictiveEngine.Score,
			"weight":       decisionResp.Breakdown.PredictiveEngine.Weight,
			"contribution": decisionResp.Breakdown.PredictiveEngine.Contribution,
		}
	}

	result := &domain.EvaluationResult{
		EntityID:              entityID,
		DataType:              req.DataType,
		RuleEngineScore:       ruleEngineScore,
		AnomalyDetectionScore: anomalyScore,
		PredictiveEngineScore: predictiveScore,
		FinalScore:            decisionResp.FinalScore,
		Decision:              decisionResp.Decision,
		Breakdown:             breakdown,
		ActionTaken:           actionTaken,
		FlaggedItemID:         flaggedItemID,
		Errors:                errors,
	}

	return result, nil
}

// invokeCallbackAsync invokes callbacks asynchronously with evaluation results
func (s *EvaluationService) invokeCallbackAsync(ctx context.Context, dataType, entityID string, decision *client.DecisionResponse, facts []map[string]interface{}) {
	go func() {
		// Construct callback payload with complete evaluation results
		payload := map[string]interface{}{
			"entity_id": entityID,
			"data_type": dataType,
			"facts":     facts,
			"evaluation": map[string]interface{}{
				"rule_engine_score": decision.Breakdown.RuleEngine.Score,
				"anomaly_score":     decision.Breakdown.AnomalyDetection.Score,
				"ml_score":          0.0,
				"final_score":       decision.FinalScore,
				"decision":          decision.Decision,
				"confidence":        decision.Confidence,
			},
			"timestamp": time.Now().Format(time.RFC3339),
		}

		// Invoke callbacks - this is how clients receive evaluation results
		err := s.callbackRepo.SendCallback(ctx, dataType, payload)
		if err != nil {
			fmt.Printf("Warning: failed to send callbacks: %v\n", err)
		} else {
			fmt.Printf("Callbacks sent successfully for entity %s with decision %s\n", entityID, decision.Decision)
		}
	}()
}

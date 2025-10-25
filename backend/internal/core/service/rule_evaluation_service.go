package service

import (
	"context"
	"fmt"
	"log"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/client"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

type RuleEvaluationService struct {
	ruleEngineClient   *client.RuleEngineClient
	flaggedItemRepo    port.FlaggedItemRepository
	flaggedItemService *FlaggedItemService
}

func NewRuleEvaluationService(ruleEngineClient *client.RuleEngineClient, flaggedItemRepo port.FlaggedItemRepository, flaggedItemService *FlaggedItemService) *RuleEvaluationService {
	return &RuleEvaluationService{
		ruleEngineClient:   ruleEngineClient,
		flaggedItemRepo:    flaggedItemRepo,
		flaggedItemService: flaggedItemService,
	}
}

func (s *RuleEvaluationService) EvaluateData(ctx context.Context, dataType string, data []map[string]interface{}) error {
	// Evaluate data against rules
	response, err := s.ruleEngineClient.Evaluate(dataType, data)
	if err != nil {
		return fmt.Errorf("failed to evaluate data: %w", err)
	}

	// Log the risk score for monitoring
	log.Printf("Data type %s: Risk Score %.2f", dataType, response.RiskScore)

	// Check if there are violations or high risk
	if len(response.Violations) == 0 && response.RiskScore < 20 {
		log.Printf("No violations found for data type %s", dataType)
		return nil
	}

	// Create flagged item for each violation
	for _, violation := range response.Violations {
		flaggedItemReq := domain.CreateFlaggedItemRequest{
			Type:      dataType,
			DataID:    response.EntityID,
			Reason:    violation.Description,
			RiskScore: response.RiskScore,
			Details:   fmt.Sprintf("Rule: %s, Weight: %d", violation.Code, violation.Weight),
			FlaggedBy: "rule-engine",
		}

		// Add rule engine score to details
		if response.Metadata != nil {
			if score, ok := response.Metadata["ruleEngineScore"]; ok {
				flaggedItemReq.Details += fmt.Sprintf(", Rule Engine Score: %v", score)
			}
		}

		_, err := s.flaggedItemService.CreateFlaggedItem(ctx, flaggedItemReq)
		if err != nil {
			log.Printf("Failed to create flagged item for violation %s: %v", violation.Code, err)
			continue
		}

		log.Printf("Created flagged item for %s violation: %s", dataType, violation.Code)
	}

	return nil
}

func (s *RuleEvaluationService) EvaluateCustomDataType(ctx context.Context, dataType string, data []map[string]interface{}) error {
	return s.EvaluateData(ctx, dataType, data)
}

package service

import (
	"context"
	"fmt"
	"log"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/client"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

// RuleEvaluationService handles rule evaluation and flagged item creation
type RuleEvaluationService struct {
	ruleEngineClient   *client.RuleEngineClient
	flaggedItemRepo    port.FlaggedItemRepository
	flaggedItemService *FlaggedItemService
}

// NewRuleEvaluationService creates a new rule evaluation service
func NewRuleEvaluationService(ruleEngineClient *client.RuleEngineClient, flaggedItemRepo port.FlaggedItemRepository, flaggedItemService *FlaggedItemService) *RuleEvaluationService {
	return &RuleEvaluationService{
		ruleEngineClient:   ruleEngineClient,
		flaggedItemRepo:    flaggedItemRepo,
		flaggedItemService: flaggedItemService,
	}
}

// EvaluateData evaluates data against rules and creates flagged items if violations are found
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
			Type:      s.mapDataTypeToFlaggedItemType(dataType),
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

// EvaluateTransaction evaluates transaction data
func (s *RuleEvaluationService) EvaluateTransaction(ctx context.Context, transactionData []map[string]interface{}) error {
	return s.EvaluateData(ctx, "transaction", transactionData)
}

// EvaluateKYC evaluates KYC data
func (s *RuleEvaluationService) EvaluateKYC(ctx context.Context, kycData []map[string]interface{}) error {
	return s.EvaluateData(ctx, "kyc", kycData)
}

// EvaluateLoan evaluates loan data
func (s *RuleEvaluationService) EvaluateLoan(ctx context.Context, loanData []map[string]interface{}) error {
	return s.EvaluateData(ctx, "loan", loanData)
}

// EvaluateCredit evaluates credit data
func (s *RuleEvaluationService) EvaluateCredit(ctx context.Context, creditData []map[string]interface{}) error {
	return s.EvaluateData(ctx, "credit", creditData)
}

// EvaluateRepayment evaluates repayment data
func (s *RuleEvaluationService) EvaluateRepayment(ctx context.Context, repaymentData []map[string]interface{}) error {
	return s.EvaluateData(ctx, "repayment", repaymentData)
}

// EvaluateCustomDataType evaluates data with custom data type
func (s *RuleEvaluationService) EvaluateCustomDataType(ctx context.Context, dataType string, data []map[string]interface{}) error {
	return s.EvaluateData(ctx, dataType, data)
}

// mapDataTypeToFlaggedItemType maps rule engine data types to flagged item types
func (s *RuleEvaluationService) mapDataTypeToFlaggedItemType(dataType string) string {
	switch dataType {
	case "transaction":
		return domain.TypeTransactions
	case "kyc":
		return domain.TypeKYC
	case "loan_request":
		return domain.TypeLoanRequests
	case "credit":
		return domain.TypeCreditHistory
	case "repayment":
		return domain.TypeRepayments
	default:
		// For custom data types, use the data type as is
		return dataType
	}
}

// GetRuleEngineClient returns the rule engine client
func (s *RuleEvaluationService) GetRuleEngineClient() *client.RuleEngineClient {
	return s.ruleEngineClient
}

// HealthCheck checks if the rule engine is healthy
func (s *RuleEvaluationService) HealthCheck() error {
	return s.ruleEngineClient.HealthCheck()
}

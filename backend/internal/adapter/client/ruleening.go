package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// RuleEngineClient handles communication with the rule engine service
type RuleEngineClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewRuleEngineClient creates a new rule engine client
func NewRuleEngineClient(baseURL string) *RuleEngineClient {
	return &RuleEngineClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// EvaluationRequest represents a request to evaluate facts
type EvaluationRequest struct {
	DataType string                   `json:"dataType"`
	Facts    []map[string]interface{} `json:"facts"`
}

// EvaluationResponse represents the response from rule evaluation
type EvaluationResponse struct {
	EntityID   string                 `json:"entityId"`
	RiskScore  float64                `json:"riskScore"`
	Violations []Violation            `json:"violations"`
	Verdict    string                 `json:"verdict"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
}

// Violation represents a rule violation
type Violation struct {
	Code        string `json:"code"`
	Weight      int    `json:"weight"`
	Description string `json:"description"`
}

// EvaluateTransaction evaluates transaction data against rules
func (c *RuleEngineClient) EvaluateTransaction(facts []map[string]interface{}) (*EvaluationResponse, error) {
	req := EvaluationRequest{
		DataType: "transaction",
		Facts:    facts,
	}
	return c.evaluate("/api/evaluate/transaction", req)
}

// EvaluateKYC evaluates KYC data against rules
func (c *RuleEngineClient) EvaluateKYC(facts []map[string]interface{}) (*EvaluationResponse, error) {
	req := EvaluationRequest{
		DataType: "kyc",
		Facts:    facts,
	}
	return c.evaluate("/api/evaluate/kyc", req)
}

// EvaluateLoan evaluates loan data against rules
func (c *RuleEngineClient) EvaluateLoan(facts []map[string]interface{}) (*EvaluationResponse, error) {
	req := EvaluationRequest{
		DataType: "loan",
		Facts:    facts,
	}
	return c.evaluate("/api/evaluate/loan", req)
}

// EvaluateCredit evaluates credit data against rules
func (c *RuleEngineClient) EvaluateCredit(facts []map[string]interface{}) (*EvaluationResponse, error) {
	req := EvaluationRequest{
		DataType: "credit",
		Facts:    facts,
	}
	return c.evaluate("/api/evaluate/credit", req)
}

// EvaluateRepayment evaluates repayment data against rules
func (c *RuleEngineClient) EvaluateRepayment(facts []map[string]interface{}) (*EvaluationResponse, error) {
	req := EvaluationRequest{
		DataType: "repayment",
		Facts:    facts,
	}
	return c.evaluate("/api/evaluate/repayment", req)
}

// EvaluateGeneric evaluates any data type against rules
func (c *RuleEngineClient) EvaluateGeneric(dataType string, facts []map[string]interface{}) (*EvaluationResponse, error) {
	req := EvaluationRequest{
		DataType: dataType,
		Facts:    facts,
	}
	return c.evaluate("/api/evaluate/generic", req)
}

// evaluate makes a generic evaluation request
func (c *RuleEngineClient) evaluate(endpoint string, req EvaluationRequest) (*EvaluationResponse, error) {
	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	url := c.baseURL + endpoint
	httpReq, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("rule engine returned status %d: %s", resp.StatusCode, string(body))
	}

	var result struct {
		Success  bool               `json:"success"`
		Response EvaluationResponse `json:"response"`
		Error    string             `json:"error,omitempty"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	if !result.Success {
		return nil, fmt.Errorf("rule engine error: %s", result.Error)
	}

	return &result.Response, nil
}

// HealthCheck checks if the rule engine is healthy
func (c *RuleEngineClient) HealthCheck() error {
	url := c.baseURL + "/health"
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return fmt.Errorf("failed to check health: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("rule engine health check failed with status %d", resp.StatusCode)
	}

	return nil
}

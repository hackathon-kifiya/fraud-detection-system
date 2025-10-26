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

// Evaluate evaluates any data type against rules using the new dynamic API
func (c *RuleEngineClient) Evaluate(dataType string, facts []map[string]interface{}) (*EvaluationResponse, error) {
	req := EvaluationRequest{
		DataType: dataType,
		Facts:    facts,
	}
	return c.evaluate("/evaluate", req)
}

// EvaluateTransaction evaluates transaction data against rules
func (c *RuleEngineClient) EvaluateTransaction(facts []map[string]interface{}) (*EvaluationResponse, error) {
	return c.Evaluate("transaction", facts)
}

// EvaluateKYC evaluates KYC data against rules
func (c *RuleEngineClient) EvaluateKYC(facts []map[string]interface{}) (*EvaluationResponse, error) {
	return c.Evaluate("kyc", facts)
}

// EvaluateLoan evaluates loan data against rules
func (c *RuleEngineClient) EvaluateLoan(facts []map[string]interface{}) (*EvaluationResponse, error) {
	return c.Evaluate("loan", facts)
}

// EvaluateCredit evaluates credit data against rules
func (c *RuleEngineClient) EvaluateCredit(facts []map[string]interface{}) (*EvaluationResponse, error) {
	return c.Evaluate("credit", facts)
}

// EvaluateRepayment evaluates repayment data against rules
func (c *RuleEngineClient) EvaluateRepayment(facts []map[string]interface{}) (*EvaluationResponse, error) {
	return c.Evaluate("repayment", facts)
}

// EvaluateGeneric evaluates any data type against rules (deprecated, use Evaluate)
func (c *RuleEngineClient) EvaluateGeneric(dataType string, facts []map[string]interface{}) (*EvaluationResponse, error) {
	return c.Evaluate(dataType, facts)
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

// makeRequest is a generic method for making HTTP requests
func (c *RuleEngineClient) makeRequest(method, endpoint string, req interface{}, resp interface{}) error {
	url := c.baseURL + endpoint

	jsonData, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	httpReq, err := http.NewRequest(method, url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")

	httpResp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return fmt.Errorf("failed to make request: %w", err)
	}
	defer httpResp.Body.Close()

	if httpResp.StatusCode != http.StatusOK {
		return fmt.Errorf("rule engine returned status %d", httpResp.StatusCode)
	}

	if err := json.NewDecoder(httpResp.Body).Decode(resp); err != nil {
		return fmt.Errorf("failed to decode response: %w", err)
	}

	return nil
}

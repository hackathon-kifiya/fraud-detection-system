package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// RiskAggregationEngineClient handles communication with the risk aggregation engine
type RiskAggregationEngineClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewRiskAggregationEngineClient creates a new risk aggregation engine client
func NewRiskAggregationEngineClient(baseURL string) *RiskAggregationEngineClient {
	return &RiskAggregationEngineClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// RiskAggregationRequest represents a request for risk aggregation
type RiskAggregationRequest struct {
	EntityID          string                   `json:"entity_id"`
	EntityType        string                   `json:"entity_type"`
	RiskScores        []map[string]interface{} `json:"risk_scores"`
	Weights           map[string]float64       `json:"weights,omitempty"`
	AggregationMethod string                   `json:"aggregation_method,omitempty"`
}

// RiskAggregationResponse represents the response from risk aggregation
type RiskAggregationResponse struct {
	Success        bool                   `json:"success"`
	EntityID       string                 `json:"entity_id"`
	EntityType     string                 `json:"entity_type"`
	AggregatedRisk float64                `json:"aggregated_risk"`
	RiskLevel      string                 `json:"risk_level"`
	Components     map[string]interface{} `json:"components"`
	Recommendation string                 `json:"recommendation"`
}

// AggregateRisk aggregates risk scores from multiple sources
func (c *RiskAggregationEngineClient) AggregateRisk(entityID, entityType string, riskScores []map[string]interface{}, weights map[string]float64, aggregationMethod string) (*RiskAggregationResponse, error) {
	req := RiskAggregationRequest{
		EntityID:          entityID,
		EntityType:        entityType,
		RiskScores:        riskScores,
		Weights:           weights,
		AggregationMethod: aggregationMethod,
	}
	return c.aggregate("/aggregate", req)
}

// aggregate makes a request to the risk aggregation engine
func (c *RiskAggregationEngineClient) aggregate(endpoint string, req interface{}) (*RiskAggregationResponse, error) {
	url := c.baseURL + endpoint

	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

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

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("risk aggregation engine returned status %d", resp.StatusCode)
	}

	var response RiskAggregationResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &response, nil
}

// HealthCheck checks if the risk aggregation engine is healthy
func (c *RiskAggregationEngineClient) HealthCheck() error {
	resp, err := c.httpClient.Get(c.baseURL + "/health")
	if err != nil {
		return fmt.Errorf("failed to check health: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("risk aggregation engine health check failed with status %d", resp.StatusCode)
	}

	return nil
}

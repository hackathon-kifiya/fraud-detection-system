package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// DecisionServiceClient handles communication with the decision service
type DecisionServiceClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewDecisionServiceClient creates a new decision service client
func NewDecisionServiceClient(baseURL string) *DecisionServiceClient {
	return &DecisionServiceClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// DecisionConfigModel represents the decision service configuration
type DecisionConfigModel struct {
	ModelBasedThresholds   bool    `json:"model_based_thresholds"`
	AutoApproveThreshold   float64 `json:"auto_approve_threshold"`
	AutoRejectThreshold    float64 `json:"auto_reject_threshold"`
	ModelBasedScoring      bool    `json:"model_based_scoring"`
	RuleEngineWeight       float64 `json:"rule_engine_weight"`
	AnomalyDetectionWeight float64 `json:"anomaly_detection_weight"`
	PredictiveEngineWeight float64 `json:"predictive_engine_weight"`
}

// DecisionRequest represents a request for a decision
type DecisionRequest struct {
	EntityID              string  `json:"entity_id"`
	RuleEngineScore       float64 `json:"rule_engine_score"`
	AnomalyDetectionScore float64 `json:"anomaly_detection_score"`
	PredictiveEngineScore float64 `json:"predictive_engine_score"`
	DataType              string  `json:"data_type,omitempty"`
}

// ScoreBreakdown represents the breakdown of scores by engine
type ScoreBreakdown struct {
	RuleEngine struct {
		Score        float64 `json:"score"`
		Weight       float64 `json:"weight"`
		Contribution float64 `json:"contribution"`
	} `json:"rule_engine"`
	AnomalyDetection struct {
		Score        float64 `json:"score"`
		Weight       float64 `json:"weight"`
		Contribution float64 `json:"contribution"`
	} `json:"anomaly_detection"`
	PredictiveEngine struct {
		Score        float64 `json:"score"`
		Weight       float64 `json:"weight"`
		Contribution float64 `json:"contribution"`
	} `json:"predictive_engine"`
}

// DecisionResponse represents the response from decision service
type DecisionResponse struct {
	EntityID          string         `json:"entity_id"`
	FinalScore        float64        `json:"final_score"`
	FinalScorePercent float64        `json:"final_score_percent"`
	Decision          string         `json:"decision"`
	Breakdown         ScoreBreakdown `json:"breakdown"`
	Confidence        float64        `json:"confidence"`
}

// ConfigUpdateResponse represents the response from config update
type ConfigUpdateResponse struct {
	Success bool                `json:"success"`
	Message string              `json:"message"`
	Config  DecisionConfigModel `json:"config"`
}

// GetConfig retrieves the current decision service configuration
func (c *DecisionServiceClient) GetConfig() (*DecisionConfigModel, error) {
	url := c.baseURL + "/config"

	httpReq, err := http.NewRequest("GET", url, nil)
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
		return nil, fmt.Errorf("decision service returned status %d", resp.StatusCode)
	}

	var config DecisionConfigModel
	if err := json.NewDecoder(resp.Body).Decode(&config); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &config, nil
}

// UpdateConfig updates the decision service configuration
func (c *DecisionServiceClient) UpdateConfig(config DecisionConfigModel) (*DecisionConfigModel, error) {
	url := c.baseURL + "/config"

	jsonData, err := json.Marshal(config)
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
		return nil, fmt.Errorf("decision service returned status %d", resp.StatusCode)
	}

	var result ConfigUpdateResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	if !result.Success {
		return nil, fmt.Errorf("failed to update config: %s", result.Message)
	}

	return &result.Config, nil
}

// MakeDecision makes a decision based on scores from multiple engines
func (c *DecisionServiceClient) MakeDecision(entityID string, ruleEngineScore, anomalyDetectionScore, predictiveEngineScore float64, dataType string) (*DecisionResponse, error) {
	req := DecisionRequest{
		EntityID:              entityID,
		RuleEngineScore:       ruleEngineScore,
		AnomalyDetectionScore: anomalyDetectionScore,
		PredictiveEngineScore: predictiveEngineScore,
		DataType:              dataType,
	}
	return c.decide("/decide", req)
}

// decide makes a request to the decision service
func (c *DecisionServiceClient) decide(endpoint string, req DecisionRequest) (*DecisionResponse, error) {
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
		return nil, fmt.Errorf("decision service returned status %d", resp.StatusCode)
	}

	var response DecisionResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &response, nil
}

// MergedDataTypeConfig represents merged configuration for a data type
type MergedDataTypeConfig struct {
	DataType         string              `json:"data_type"`
	Config           DecisionConfigModel `json:"config"`
	IsCustom         bool                `json:"is_custom"`
	OverriddenFields []string            `json:"overridden_fields"`
}

// DataTypeDecisionConfig represents data-type-specific config overrides
type DataTypeDecisionConfig struct {
	DataType               string   `json:"data_type"`
	AutoApproveThreshold   *float64 `json:"auto_approve_threshold,omitempty"`
	AutoRejectThreshold    *float64 `json:"auto_reject_threshold,omitempty"`
	RuleEngineWeight       *float64 `json:"rule_engine_weight,omitempty"`
	AnomalyDetectionWeight *float64 `json:"anomaly_detection_weight,omitempty"`
	PredictiveEngineWeight *float64 `json:"predictive_engine_weight,omitempty"`
	ModelBasedScoring      *bool    `json:"model_based_scoring,omitempty"`
	ModelBasedThresholds   *bool    `json:"model_based_thresholds,omitempty"`
}

// GetDataTypeConfig retrieves merged configuration for a specific data type
func (c *DecisionServiceClient) GetDataTypeConfig(dataType string) (*MergedDataTypeConfig, error) {
	url := fmt.Sprintf("%s/config/data-types/%s", c.baseURL, dataType)

	httpReq, err := http.NewRequest("GET", url, nil)
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
		return nil, fmt.Errorf("decision service returned status %d", resp.StatusCode)
	}

	var config MergedDataTypeConfig
	if err := json.NewDecoder(resp.Body).Decode(&config); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &config, nil
}

// UpdateDataTypeConfig updates data-type-specific configuration
func (c *DecisionServiceClient) UpdateDataTypeConfig(dataType string, config DataTypeDecisionConfig) (*DataTypeDecisionConfig, error) {
	url := fmt.Sprintf("%s/config/data-types/%s", c.baseURL, dataType)

	jsonData, err := json.Marshal(config)
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
		return nil, fmt.Errorf("decision service returned status %d", resp.StatusCode)
	}

	var result DataTypeDecisionConfig
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &result, nil
}

// GetAllDataTypeConfigs retrieves all data types with custom configs
func (c *DecisionServiceClient) GetAllDataTypeConfigs() ([]string, error) {
	url := c.baseURL + "/config/data-types"

	httpReq, err := http.NewRequest("GET", url, nil)
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
		return nil, fmt.Errorf("decision service returned status %d", resp.StatusCode)
	}

	var result struct {
		DataTypes []map[string]string `json:"data_types"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	dataTypes := make([]string, len(result.DataTypes))
	for i, dt := range result.DataTypes {
		dataTypes[i] = dt["data_type"]
	}

	return dataTypes, nil
}

// DeleteDataTypeConfig deletes data-type-specific configuration
func (c *DecisionServiceClient) DeleteDataTypeConfig(dataType string) error {
	url := fmt.Sprintf("%s/config/data-types/%s", c.baseURL, dataType)

	httpReq, err := http.NewRequest("DELETE", url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("decision service returned status %d", resp.StatusCode)
	}

	return nil
}

// HealthCheck checks if the decision service is healthy
func (c *DecisionServiceClient) HealthCheck() error {
	resp, err := c.httpClient.Get(c.baseURL + "/health")
	if err != nil {
		return fmt.Errorf("failed to check health: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("decision service health check failed with status %d", resp.StatusCode)
	}

	return nil
}

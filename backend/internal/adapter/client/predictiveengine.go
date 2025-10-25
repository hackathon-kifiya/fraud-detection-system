package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// PredictiveEngineClient handles communication with the predictive engine
type PredictiveEngineClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewPredictiveEngineClient creates a new predictive engine client
func NewPredictiveEngineClient(baseURL string) *PredictiveEngineClient {
	return &PredictiveEngineClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// PredictiveRequest represents a request for predictive analysis
type PredictiveRequest struct {
	ModelType string                   `json:"model_type,omitempty"`
	Data      []map[string]interface{} `json:"data,omitempty"`
	Features  []string                 `json:"features,omitempty"`
}

// PredictiveResponse represents the response from predictive analysis
type PredictiveResponse struct {
	Success     bool                     `json:"success"`
	Predictions []map[string]interface{} `json:"predictions"`
	Confidence  float64                  `json:"confidence"`
	ModelInfo   map[string]interface{}   `json:"model_info"`
}

// Predict makes predictions using the predictive engine
func (c *PredictiveEngineClient) Predict(modelType string, data []map[string]interface{}, features []string) (*PredictiveResponse, error) {
	req := PredictiveRequest{
		ModelType: modelType,
		Data:      data,
		Features:  features,
	}
	return c.predict("/predict", req)
}

// predict makes a request to the predictive engine
func (c *PredictiveEngineClient) predict(endpoint string, req interface{}) (*PredictiveResponse, error) {
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
		return nil, fmt.Errorf("predictive engine returned status %d", resp.StatusCode)
	}

	var response PredictiveResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &response, nil
}

// HealthCheck checks if the predictive engine is healthy
func (c *PredictiveEngineClient) HealthCheck() error {
	resp, err := c.httpClient.Get(c.baseURL + "/health")
	if err != nil {
		return fmt.Errorf("failed to check health: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("predictive engine health check failed with status %d", resp.StatusCode)
	}

	return nil
}

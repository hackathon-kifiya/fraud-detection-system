package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// AnomalyDetectionEngineClient handles communication with the anomaly detection engine
type AnomalyDetectionEngineClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewAnomalyDetectionEngineClient creates a new anomaly detection engine client
func NewAnomalyDetectionEngineClient(baseURL string) *AnomalyDetectionEngineClient {
	return &AnomalyDetectionEngineClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// AnomalyDetectionRequest represents a request to detect anomalies
type AnomalyDetectionRequest struct {
	DaysBack int                      `json:"days_back,omitempty"`
	Data     []map[string]interface{} `json:"data,omitempty"`
}

// AnomalyDetectionResponse represents the response from anomaly detection
type AnomalyDetectionResponse struct {
	Success bool                   `json:"success"`
	Message string                 `json:"message"`
	Result  map[string]interface{} `json:"result"`
}

// DetectAnomalies detects anomalies in the provided data
func (c *AnomalyDetectionEngineClient) DetectAnomalies(daysBack int, data []map[string]interface{}) (*AnomalyDetectionResponse, error) {
	req := AnomalyDetectionRequest{
		DaysBack: daysBack,
		Data:     data,
	}
	return c.detect("/detect", req)
}

// detect makes a request to the anomaly detection engine
func (c *AnomalyDetectionEngineClient) detect(endpoint string, req interface{}) (*AnomalyDetectionResponse, error) {
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
		return nil, fmt.Errorf("anomaly detection engine returned status %d", resp.StatusCode)
	}

	var response AnomalyDetectionResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &response, nil
}

// HealthCheck checks if the anomaly detection engine is healthy
func (c *AnomalyDetectionEngineClient) HealthCheck() error {
	resp, err := c.httpClient.Get(c.baseURL + "/health")
	if err != nil {
		return fmt.Errorf("failed to check health: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("anomaly detection engine health check failed with status %d", resp.StatusCode)
	}

	return nil
}

package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// RuleEngineDataTypeClient handles data type synchronization with the rule engine
type RuleEngineDataTypeClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewRuleEngineDataTypeClient creates a new data type client
func NewRuleEngineDataTypeClient(baseURL string) *RuleEngineDataTypeClient {
	return &RuleEngineDataTypeClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// DataTypeRequest represents a request to create/update a data type in the rule engine
type DataTypeRequest struct {
	DataType         string                 `json:"dataType"`
	Name             string                 `json:"name"`
	Description      string                 `json:"description"`
	SchemaDefinition map[string]interface{} `json:"schemaDefinition"`
	SampleData       map[string]interface{} `json:"sampleData,omitempty"`
	CreatedBy        string                 `json:"createdBy,omitempty"`
	UpdatedBy        string                 `json:"updatedBy,omitempty"`
}

// DataTypeResponse represents the response from the rule engine
type DataTypeResponse struct {
	ID               string                 `json:"id"`
	DataType         string                 `json:"dataType"`
	Name             string                 `json:"name"`
	Description      string                 `json:"description"`
	SchemaDefinition map[string]interface{} `json:"schemaDefinition"`
	SampleData       map[string]interface{} `json:"sampleData,omitempty"`
	Status           string                 `json:"status"`
	CreatedAt        string                 `json:"createdAt"`
	UpdatedAt        string                 `json:"updatedAt"`
	CreatedBy        string                 `json:"createdBy"`
	UpdatedBy        string                 `json:"updatedBy"`
}

// CreateDataType creates a data type in the rule engine
func (c *RuleEngineDataTypeClient) CreateDataType(req DataTypeRequest) (*DataTypeResponse, error) {
	url := c.baseURL + "/api/data-types"

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

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("rule engine returned status %d: %s", resp.StatusCode, string(body))
	}

	var dataTypeResp DataTypeResponse
	if err := json.Unmarshal(body, &dataTypeResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &dataTypeResp, nil
}

// UpdateDataType updates a data type in the rule engine by name
func (c *RuleEngineDataTypeClient) UpdateDataType(dataType string, req DataTypeRequest) (*DataTypeResponse, error) {
	url := c.baseURL + "/api/data-types/by-name/" + dataType

	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	httpReq, err := http.NewRequest("PUT", url, bytes.NewBuffer(jsonData))
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

	var dataTypeResp DataTypeResponse
	if err := json.Unmarshal(body, &dataTypeResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &dataTypeResp, nil
}

// DeleteDataType is disabled - data types cannot be deleted
func (c *RuleEngineDataTypeClient) DeleteDataType(dataType string) error {
	return fmt.Errorf("data type deletion is not allowed")
}

// GetDataTypeByName retrieves a data type by name from the rule engine
func (c *RuleEngineDataTypeClient) GetDataTypeByName(dataType string) (*DataTypeResponse, error) {
	url := c.baseURL + "/api/data-types/by-name/" + dataType

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

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("rule engine returned status %d: %s", resp.StatusCode, string(body))
	}

	var dataTypeResp DataTypeResponse
	if err := json.Unmarshal(body, &dataTypeResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &dataTypeResp, nil
}

// GetAllDataTypes retrieves all data types from the rule engine
func (c *RuleEngineDataTypeClient) GetAllDataTypes() ([]DataTypeResponse, error) {
	url := c.baseURL + "/api/data-types"

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

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("rule engine returned status %d: %s", resp.StatusCode, string(body))
	}

	var dataTypes []DataTypeResponse
	if err := json.Unmarshal(body, &dataTypes); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return dataTypes, nil
}

// SyncDataType syncs a data type from backend to rule engine
// It attempts to update if exists, otherwise creates new
func (c *RuleEngineDataTypeClient) SyncDataType(req DataTypeRequest) error {
	// Check if data type exists
	_, err := c.GetDataTypeByName(req.DataType)
	if err != nil {
		// Doesn't exist, create it
		_, err := c.CreateDataType(req)
		if err != nil {
			return fmt.Errorf("failed to create data type in rule engine: %w", err)
		}
		return nil
	}

	// Exists, update it
	_, err = c.UpdateDataType(req.DataType, req)
	if err != nil {
		return fmt.Errorf("failed to update data type in rule engine: %w", err)
	}

	return nil
}

// HealthCheck checks if the rule engine data type service is healthy
func (c *RuleEngineDataTypeClient) HealthCheck() error {
	resp, err := c.httpClient.Get(c.baseURL + "/health")
	if err != nil {
		return fmt.Errorf("failed to check health: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("rule engine health check failed with status %d", resp.StatusCode)
	}

	return nil
}

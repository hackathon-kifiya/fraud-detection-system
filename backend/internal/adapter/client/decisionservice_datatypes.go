package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// DecisionServiceDataTypeClient handles data type synchronization with the decision service
type DecisionServiceDataTypeClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewDecisionServiceDataTypeClient creates a new data type client for decision service
func NewDecisionServiceDataTypeClient(baseURL string) *DecisionServiceDataTypeClient {
	return &DecisionServiceDataTypeClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// DecisionDataTypeRequest represents a request to create/update a data type in the decision service
type DecisionDataTypeRequest struct {
	DataType         string                 `json:"data_type"`
	Name             string                 `json:"name"`
	Description      string                 `json:"description"`
	SchemaDefinition map[string]interface{} `json:"schema_definition"`
	SampleData       map[string]interface{} `json:"sample_data,omitempty"`
	Status           string                 `json:"status"`
	CreatedBy        string                 `json:"created_by"`
	UpdatedBy        string                 `json:"updated_by,omitempty"`
}

// DecisionDataTypeResponse represents the response from the decision service
type DecisionDataTypeResponse struct {
	DataType         string                 `json:"data_type"`
	Name             string                 `json:"name"`
	Description      string                 `json:"description"`
	SchemaDefinition map[string]interface{} `json:"schema_definition"`
	SampleData       map[string]interface{} `json:"sample_data,omitempty"`
	Status           string                 `json:"status"`
	CreatedAt        string                 `json:"created_at"`
	UpdatedAt        string                 `json:"updated_at"`
	CreatedBy        string                 `json:"created_by"`
	UpdatedBy        string                 `json:"updated_by,omitempty"`
}

// SyncDataType syncs a data type to the decision service
func (c *DecisionServiceDataTypeClient) SyncDataType(req DecisionDataTypeRequest) error {
	// Check if data type already exists
	exists, err := c.dataTypeExists(req.DataType)
	if err != nil {
		return fmt.Errorf("failed to check if data type exists: %w", err)
	}

	if exists {
		// Update existing data type
		return c.updateDataType(req.DataType, req)
	}

	// Create new data type
	return c.createDataType(req)
}

func (c *DecisionServiceDataTypeClient) createDataType(req DecisionDataTypeRequest) error {
	url := fmt.Sprintf("%s/data-types", c.baseURL)

	jsonData, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := c.httpClient.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create data type: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("failed to create data type: status %d, body: %s", resp.StatusCode, string(body))
	}

	return nil
}

func (c *DecisionServiceDataTypeClient) updateDataType(dataType string, req DecisionDataTypeRequest) error {
	url := fmt.Sprintf("%s/data-types/%s", c.baseURL, dataType)

	jsonData, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	httpReq, err := http.NewRequest("PUT", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return fmt.Errorf("failed to update data type: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("failed to update data type: status %d, body: %s", resp.StatusCode, string(body))
	}

	return nil
}

func (c *DecisionServiceDataTypeClient) dataTypeExists(dataType string) (bool, error) {
	url := fmt.Sprintf("%s/data-types/%s", c.baseURL, dataType)

	resp, err := c.httpClient.Get(url)
	if err != nil {
		return false, fmt.Errorf("failed to check data type: %w", err)
	}
	defer resp.Body.Close()

	return resp.StatusCode == http.StatusOK, nil
}

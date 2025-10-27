package client

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// DataManagementClient handles all interactions with the Data Management Service
type DataManagementClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewDataManagementClient creates a new data management service client
func NewDataManagementClient(baseURL string) *DataManagementClient {
	return &DataManagementClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// DataManagementDataTypeResponse represents a data type from the Data Management Service
type DataManagementDataTypeResponse struct {
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

// GetAllDataTypes fetches all data types from the Data Management Service
func (c *DataManagementClient) GetAllDataTypes() ([]DataManagementDataTypeResponse, error) {
	url := fmt.Sprintf("%s/data-types", c.baseURL)

	resp, err := c.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch data types: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to fetch data types: status %d, body: %s", resp.StatusCode, string(body))
	}

	var dataTypes []DataManagementDataTypeResponse
	if err := json.NewDecoder(resp.Body).Decode(&dataTypes); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return dataTypes, nil
}

// GetDataType fetches a specific data type from the Data Management Service
func (c *DataManagementClient) GetDataType(dataType string) (*DataManagementDataTypeResponse, error) {
	url := fmt.Sprintf("%s/data-types/%s", c.baseURL, dataType)

	resp, err := c.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch data type: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return nil, fmt.Errorf("data type '%s' not found", dataType)
	}

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to fetch data type: status %d, body: %s", resp.StatusCode, string(body))
	}

	var dataTypeResponse DataManagementDataTypeResponse
	if err := json.NewDecoder(resp.Body).Decode(&dataTypeResponse); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &dataTypeResponse, nil
}

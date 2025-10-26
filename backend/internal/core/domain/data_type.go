package domain

import (
	"time"
)

// DataType represents a dynamic data type schema in the system
type DataType struct {
	ID               string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	DataType         string    `json:"data_type" gorm:"column:data_type;uniqueIndex;not null"`
	Name             string    `json:"name" gorm:"not null"`
	Description      string    `json:"description" gorm:"type:text"`
	SchemaDefinition string    `json:"schema_definition" gorm:"column:schema_definition;type:jsonb"`
	SampleData       string    `json:"sample_data" gorm:"column:sample_data;type:jsonb"`
	Status           string    `json:"status" gorm:"not null;default:'ACTIVE'"`
	CreatedAt        time.Time `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt        time.Time `json:"updated_at" gorm:"autoUpdateTime"`
	CreatedBy        string    `json:"created_by" gorm:"column:created_by"`
	UpdatedBy        string    `json:"updated_by" gorm:"column:updated_by"`
}

// TableName specifies the table name for GORM
func (DataType) TableName() string {
	return "data_types"
}

// DataTypeStatus represents the possible statuses for a data type
const (
	DataTypeStatusActive   = "ACTIVE"
	DataTypeStatusInactive = "INACTIVE"
	DataTypeStatusDraft    = "DRAFT"
)

// CreateDataTypeRequest represents the request to create a data type
type CreateDataTypeRequest struct {
	DataType         string                 `json:"data_type" binding:"required"`
	Name             string                 `json:"name" binding:"required"`
	Description      string                 `json:"description"`
	SchemaDefinition map[string]interface{} `json:"schema_definition" binding:"required"`
	SampleData       map[string]interface{} `json:"sample_data"`
	Status           string                 `json:"status"`
	CreatedBy        string                 `json:"created_by"`
}

// UpdateDataTypeRequest represents the request to update a data type
type UpdateDataTypeRequest struct {
	DataType         *string                `json:"data_type,omitempty"`
	Name             *string                `json:"name,omitempty"`
	Description      *string                `json:"description,omitempty"`
	SchemaDefinition map[string]interface{} `json:"schema_definition,omitempty"`
	SampleData       map[string]interface{} `json:"sample_data,omitempty"`
	Status           *string                `json:"status,omitempty"`
	UpdatedBy        *string                `json:"updated_by,omitempty"`
}

// DataTypeListResponse represents the response for listing data types
type DataTypeListResponse struct {
	DataTypes []DataType `json:"data_types"`
	Total     int64      `json:"total"`
	Limit     int        `json:"limit"`
	Offset    int        `json:"offset"`
}

// DataTypeSearchRequest represents a search request for data types
type DataTypeSearchRequest struct {
	Search string `json:"search"`
	Status string `json:"status,omitempty"` // Optional filter by status
}

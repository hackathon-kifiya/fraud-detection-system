package domain

import (
	"time"
)

// LabeledData represents labeled data for model retraining
type LabeledData struct {
	ID            string                 `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	EntityID      string                 `json:"entity_id" gorm:"not null"`
	DataType      string                 `json:"data_type" gorm:"not null"`
	Facts         map[string]interface{} `json:"facts" gorm:"type:jsonb"`
	Decision      string                 `json:"decision" gorm:"not null"` // "confirmed", "false_positive", "approved", "rejected"
	LabeledBy     string                 `json:"labeled_by" gorm:"not null"`
	FlaggedItemID string                 `json:"flagged_item_id,omitempty" gorm:"column:flagged_item_id"`
	CreatedAt     time.Time              `json:"created_at" gorm:"autoCreateTime"`
}

// TableName specifies the table name for GORM
func (LabeledData) TableName() string {
	return "labeled_data"
}

// CreateLabeledDataRequest represents the request to create labeled data
type CreateLabeledDataRequest struct {
	EntityID      string                 `json:"entity_id" binding:"required"`
	DataType      string                 `json:"data_type" binding:"required"`
	Facts         map[string]interface{} `json:"facts" binding:"required"`
	Decision      string                 `json:"decision" binding:"required"`
	LabeledBy     string                 `json:"labeled_by" binding:"required"`
	FlaggedItemID string                 `json:"flagged_item_id,omitempty"`
}

// LabeledDataListResponse represents paginated response
type LabeledDataListResponse struct {
	Items  []LabeledData `json:"items"`
	Total  int64         `json:"total"`
	Limit  int           `json:"limit"`
	Offset int           `json:"offset"`
}

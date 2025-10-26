package domain

import (
	"time"
)

// Callback represents a callback configuration
type Callback struct {
	ID          string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	DataType    string    `json:"data_type" gorm:"not null"`
	CallbackURL string    `json:"callback_url" gorm:"column:callback_url;not null"`
	Method      string    `json:"method" gorm:"not null;default:'POST'"`
	Headers     string    `json:"headers" gorm:"type:text"`
	IsActive    bool      `json:"is_active" gorm:"column:is_active;default:true"`
	CreatedAt   time.Time `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt   time.Time `json:"updated_at" gorm:"autoUpdateTime"`
}

// TableName specifies the table name for GORM
func (Callback) TableName() string {
	return "callbacks"
}

// CreateCallbackRequest represents the request to create a callback
type CreateCallbackRequest struct {
	DataType    string `json:"data_type" binding:"required,oneof=transactions loan_requests credit_history kyc repayments flagged_items"`
	CallbackURL string `json:"callback_url" binding:"required,url"`
	Method      string `json:"method" binding:"required,oneof=POST PUT PATCH"`
	Headers     string `json:"headers"`
	IsActive    bool   `json:"is_active"`
}

// UpdateCallbackRequest represents the request to update a callback
type UpdateCallbackRequest struct {
	DataType    *string `json:"data_type,omitempty" binding:"omitempty,oneof=transactions loan_requests credit_history kyc repayments flagged_items"`
	CallbackURL *string `json:"callback_url,omitempty" binding:"omitempty,url"`
	Method      *string `json:"method,omitempty" binding:"omitempty,oneof=POST PUT PATCH"`
	Headers     *string `json:"headers,omitempty"`
	IsActive    *bool   `json:"is_active,omitempty"`
}

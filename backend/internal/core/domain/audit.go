package domain

import (
	"time"
)

// AuditNote represents a contextual note added by an auditor
type AuditNote struct {
	ID            string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	FlaggedItemID string    `json:"flagged_item_id" gorm:"not null"`
	UserID        string    `json:"user_id" gorm:"not null"`
	NoteText      string    `json:"note_text" gorm:"type:text;not null"`
	CreatedAt     time.Time `json:"created_at" gorm:"autoCreateTime"`
}

// TableName specifies the table name for GORM
func (AuditNote) TableName() string {
	return "audit_notes"
}

// AuditLog represents an audit trail entry for tracking all review actions
type AuditLog struct {
	ID            string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	FlaggedItemID string    `json:"flagged_item_id" gorm:"not null"`
	UserID        string    `json:"user_id" gorm:"not null"`
	Action        string    `json:"action" gorm:"not null"` // "status_change", "classification", "note_added", "reviewed"
	OldStatus     *string   `json:"old_status" gorm:"column:old_status"`
	NewStatus     *string   `json:"new_status" gorm:"column:new_status"`
	Metadata      string    `json:"metadata" gorm:"type:jsonb"` // Additional context as JSON
	Timestamp     time.Time `json:"timestamp" gorm:"autoCreateTime"`
}

// TableName specifies the table name for GORM
func (AuditLog) TableName() string {
	return "audit_log"
}

// AuditLogAction constants
const (
	ActionStatusChange   = "status_change"
	ActionClassification = "classification"
	ActionNoteAdded      = "note_added"
	ActionReviewed       = "reviewed"
)

// FlaggedItemDetail represents an enhanced flagged item with original data and scores
type FlaggedItemDetail struct {
	FlaggedItem
	OriginalData    interface{} `json:"original_data"`     // Original transaction/loan/KYC/repayment data
	RuleEngineScore *float64    `json:"rule_engine_score"` // Score from rule engine
	MLScore         *float64    `json:"ml_score"`          // Score from ML model
	AnomalyScore    *float64    `json:"anomaly_score"`     // Score from anomaly detection
	AuditNotes      []AuditNote `json:"audit_notes"`       // All notes for this item
	AuditTrail      []AuditLog  `json:"audit_trail"`       // Complete audit trail
}

// ReviewClassificationRequest represents the request to classify a flagged item
type ReviewClassificationRequest struct {
	Classification string `json:"classification" binding:"required,oneof=confirmed false_positive"`
	Notes          string `json:"notes"`
}

// AuditNoteRequest represents the request to add a contextual note
type AuditNoteRequest struct {
	NoteText string `json:"note_text" binding:"required"`
}

// PersonalReviewHistoryResponse represents the response for auditor's review history
type PersonalReviewHistoryResponse struct {
	Items  []FlaggedItem `json:"items"`
	Total  int64         `json:"total"`
	Limit  int           `json:"limit"`
	Offset int           `json:"offset"`
	Stats  struct {
		TotalReviewed     int64 `json:"total_reviewed"`
		ConfirmedFraud    int64 `json:"confirmed_fraud"`
		FalsePositives    int64 `json:"false_positives"`
		AverageReviewTime int64 `json:"average_review_time_minutes"`
	} `json:"stats"`
}

// AuditStats represents auditor-specific statistics
type AuditStats struct {
	TotalReviewed     int64 `json:"total_reviewed"`
	ConfirmedFraud    int64 `json:"confirmed_fraud"`
	FalsePositives    int64 `json:"false_positives"`
	AverageReviewTime int64 `json:"average_review_time_minutes"`
	PendingReview     int64 `json:"pending_review"`
	HighRiskItems     int64 `json:"high_risk_items"`
}

// FlaggedItemListRequest represents the request for listing flagged items with filters
type FlaggedItemListRequest struct {
	Status       string   `form:"status"`
	Type         string   `form:"type"`
	RiskScoreMin *float64 `form:"risk_score_min"`
	RiskScoreMax *float64 `form:"risk_score_max"`
	SortBy       string   `form:"sort_by"`    // "created_at", "risk_score", "updated_at"
	SortOrder    string   `form:"sort_order"` // "asc", "desc"
	Limit        int      `form:"limit"`
	Offset       int      `form:"offset"`
}

// PersonalReviewHistoryRequest represents the request for personal review history
type PersonalReviewHistoryRequest struct {
	Status   string `form:"status"`
	Type     string `form:"type"`
	DateFrom string `form:"date_from"` // YYYY-MM-DD format
	DateTo   string `form:"date_to"`   // YYYY-MM-DD format
	Limit    int    `form:"limit"`
	Offset   int    `form:"offset"`
}

package domain

import (
	"time"
)

// FlaggedItem represents a flagged item in the system
type FlaggedItem struct {
	ID                string     `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	Type              string     `json:"type" gorm:"not null"`                                  // transactions, loan_requests, credit_history, kyc, repayments
	DataID            string     `json:"data_id" gorm:"not null"`                               // ID of the original data item
	Reason            string     `json:"reason" gorm:"not null"`                                // Why it was flagged
	RiskScore         float64    `json:"risk_score" gorm:"not null"`                            // Risk score (0-100)
	Status            string     `json:"status" gorm:"not null;default:'pending'"`              // pending, reviewed, confirmed, false_positive
	Details           string     `json:"details" gorm:"type:text"`                              // Additional details
	ReviewNotes       string     `json:"review_notes" gorm:"type:text"`                         // Primary review notes from auditor
	RuleEngineScore   *float64   `json:"rule_engine_score" gorm:"column:rule_engine_score"`     // Score from rule engine
	MLScore           *float64   `json:"ml_score" gorm:"column:ml_score"`                       // Score from ML model
	AnomalyScore      *float64   `json:"anomaly_score" gorm:"column:anomaly_score"`             // Score from anomaly detection
	DecisionBreakdown string     `json:"decision_breakdown" gorm:"type:text"`                   // JSON breakdown of decision aggregation
	Confidence        *float64   `json:"confidence" gorm:"column:confidence"`                   // Decision confidence (0-1)
	FinalScorePercent *float64   `json:"final_score_percent" gorm:"column:final_score_percent"` // Final score as percentage
	FlaggedBy         string     `json:"flagged_by" gorm:"not null"`                            // System or user who flagged it
	ReviewedBy        *string    `json:"reviewed_by" gorm:"column:reviewed_by"`                 // User who reviewed it
	ReviewedAt        *time.Time `json:"reviewed_at" gorm:"column:reviewed_at"`
	CreatedAt         time.Time  `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt         time.Time  `json:"updated_at" gorm:"autoUpdateTime"`
}

// TableName specifies the table name for GORM
func (FlaggedItem) TableName() string {
	return "flagged_items"
}

// FlaggedItemStatus represents the possible statuses
const (
	StatusPending       = "pending"
	StatusReviewed      = "reviewed"
	StatusConfirmed     = "confirmed"
	StatusFalsePositive = "false_positive"
)

// FlaggedItemType represents the possible types
const (
	TypeTransactions  = "transactions"
	TypeLoanRequests  = "loan_requests"
	TypeCreditHistory = "credit_history"
	TypeKYC           = "kyc"
	TypeRepayments    = "repayments"
)

// CreateFlaggedItemRequest represents the request to create a flagged item
type CreateFlaggedItemRequest struct {
	Type      string  `json:"type" binding:"required"`
	DataID    string  `json:"data_id" binding:"required"`
	Reason    string  `json:"reason" binding:"required"`
	RiskScore float64 `json:"risk_score" binding:"required,min=0,max=100"`
	Details   string  `json:"details"`
	FlaggedBy string  `json:"flagged_by" binding:"required"`
}

// UpdateFlaggedItemRequest represents the request to update a flagged item
type UpdateFlaggedItemRequest struct {
	Status     string  `json:"status" binding:"required,oneof=pending reviewed confirmed false_positive"`
	ReviewedBy *string `json:"reviewed_by"`
	Details    *string `json:"details"`
}

// FlaggedItemStats represents statistics about flagged items
type FlaggedItemStats struct {
	TotalFlagged   int64            `json:"totalFlagged"`
	PendingReview  int64            `json:"pendingReview"`
	ConfirmedFraud int64            `json:"confirmedFraud"`
	VerifiedSafe   int64            `json:"verifiedSafe"`
	FlaggedByType  map[string]int64 `json:"flaggedByType"`
	HighRiskCount  int64            `json:"highRiskCount"`
}

// FlaggedItemListResponse represents the response for listing flagged items
type FlaggedItemListResponse struct {
	Items  []FlaggedItem `json:"items"`
	Total  int64         `json:"total"`
	Limit  int           `json:"limit"`
	Offset int           `json:"offset"`
}

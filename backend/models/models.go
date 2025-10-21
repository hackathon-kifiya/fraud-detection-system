package models

import (
	"time"

	"github.com/google/uuid"
)

// Transaction represents a financial transaction
type Transaction struct {
	TxnID          uuid.UUID `json:"txn_id" db:"txn_id"`
	UserID         string    `json:"user_id" db:"user_id"`
	Amount         float64   `json:"amount" db:"amount"`
	Timestamp      time.Time `json:"timestamp" db:"timestamp"`
	Type           string    `json:"type" db:"type"`
	PaymentMethod  string    `json:"payment_method" db:"payment_method"`
	Items          string    `json:"items" db:"items"` // JSON string
	AccountBalance float64   `json:"account_balance" db:"account_balance"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
}

// LoanRequest represents a loan application
type LoanRequest struct {
	LoanID           uuid.UUID `json:"loan_id" db:"loan_id"`
	UserID           string    `json:"user_id" db:"user_id"`
	AmountRequested  float64   `json:"amount_requested" db:"amount_requested"`
	Purpose          string    `json:"purpose" db:"purpose"`
	RequestTimestamp time.Time `json:"request_timestamp" db:"request_timestamp"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
}

// CreditHistory represents user's credit information
type CreditHistory struct {
	UserID        string    `json:"user_id" db:"user_id"`
	CreditScore   int       `json:"credit_score" db:"credit_score"`
	PastLoans     string    `json:"past_loans" db:"past_loans"` // JSON string
	DefaultsCount int       `json:"defaults_count" db:"defaults_count"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
}

// KYC represents Know Your Customer data
type KYC struct {
	UserID                string     `json:"user_id" db:"user_id"`
	VerifiedStatus        bool       `json:"verified_status" db:"verified_status"`
	Documents             string     `json:"documents" db:"documents"` // JSON string
	VerificationTimestamp *time.Time `json:"verification_timestamp" db:"verification_timestamp"`
	CreatedAt             time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt             time.Time  `json:"updated_at" db:"updated_at"`
}

// Repayment represents a loan repayment
type Repayment struct {
	RepaymentID uuid.UUID `json:"repayment_id" db:"repayment_id"`
	UserID      string    `json:"user_id" db:"user_id"`
	LoanID      uuid.UUID `json:"loan_id" db:"loan_id"`
	Amount      float64   `json:"amount" db:"amount"`
	Timestamp   time.Time `json:"timestamp" db:"timestamp"`
	Status      string    `json:"status" db:"status"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

// FlaggedItem represents a flagged item for review
type FlaggedItem struct {
	ID         uuid.UUID  `json:"id" db:"id"`
	Type       string     `json:"type" db:"type"`
	RefID      uuid.UUID  `json:"ref_id" db:"ref_id"`
	UserID     string     `json:"user_id" db:"user_id"`
	Score      float64    `json:"score" db:"score"`
	Reasons    string     `json:"reasons" db:"reasons"` // JSON string
	Status     string     `json:"status" db:"status"`
	VerifiedAt *time.Time `json:"verified_at" db:"verified_at"`
	CreatedAt  time.Time  `json:"created_at" db:"created_at"`
}

// UploadResponse represents the response for file uploads
type UploadResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
	Count   int    `json:"count,omitempty"`
	Error   string `json:"error,omitempty"`
}

// DetectionResponse represents the response for fraud detection
type DetectionResponse struct {
	Success bool                   `json:"success"`
	Message string                 `json:"message"`
	Result  map[string]interface{} `json:"result,omitempty"`
	Error   string                 `json:"error,omitempty"`
}

// FlaggedItemsResponse represents the response for flagged items
type FlaggedItemsResponse struct {
	Success bool          `json:"success"`
	Items   []FlaggedItem `json:"items,omitempty"`
	Total   int           `json:"total,omitempty"`
	Error   string        `json:"error,omitempty"`
}

// VerifyRequest represents the request to verify a flagged item
type VerifyRequest struct {
	Status string `json:"status" binding:"required"`
}

// VerifyResponse represents the response for verification
type VerifyResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
	Error   string `json:"error,omitempty"`
}

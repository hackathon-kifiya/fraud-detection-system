package handlers

import (
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"time"

	"fraud-detection-backend/db"
	"fraud-detection-backend/models"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

// UploadHandler handles file uploads and CSV processing
type UploadHandler struct {
	db *db.DB
}

// NewUploadHandler creates a new upload handler
func NewUploadHandler(database *db.DB) *UploadHandler {
	return &UploadHandler{db: database}
}

// UploadTransactions handles transaction CSV uploads
func (h *UploadHandler) UploadTransactions(c *gin.Context) {
	file, _, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   "No file provided",
		})
		return
	}
	defer file.Close()

	transactions, err := h.parseTransactionCSV(file)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to parse CSV: %v", err),
		})
		return
	}

	count, err := h.insertTransactions(c.Request.Context(), transactions)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to insert transactions: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.UploadResponse{
		Success: true,
		Message: "Transactions uploaded successfully",
		Count:   count,
	})
}

// UploadLoanRequests handles loan request CSV uploads
func (h *UploadHandler) UploadLoanRequests(c *gin.Context) {
	file, _, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   "No file provided",
		})
		return
	}
	defer file.Close()

	loans, err := h.parseLoanRequestCSV(file)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to parse CSV: %v", err),
		})
		return
	}

	count, err := h.insertLoanRequests(c.Request.Context(), loans)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to insert loan requests: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.UploadResponse{
		Success: true,
		Message: "Loan requests uploaded successfully",
		Count:   count,
	})
}

// UploadCreditHistory handles credit history CSV uploads
func (h *UploadHandler) UploadCreditHistory(c *gin.Context) {
	file, _, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   "No file provided",
		})
		return
	}
	defer file.Close()

	creditHistory, err := h.parseCreditHistoryCSV(file)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to parse CSV: %v", err),
		})
		return
	}

	count, err := h.insertCreditHistory(c.Request.Context(), creditHistory)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to insert credit history: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.UploadResponse{
		Success: true,
		Message: "Credit history uploaded successfully",
		Count:   count,
	})
}

// UploadKYC handles KYC CSV uploads
func (h *UploadHandler) UploadKYC(c *gin.Context) {
	file, _, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   "No file provided",
		})
		return
	}
	defer file.Close()

	kyc, err := h.parseKYCCSV(file)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to parse CSV: %v", err),
		})
		return
	}

	count, err := h.insertKYC(c.Request.Context(), kyc)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to insert KYC: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.UploadResponse{
		Success: true,
		Message: "KYC uploaded successfully",
		Count:   count,
	})
}

// UploadRepayments handles repayment CSV uploads
func (h *UploadHandler) UploadRepayments(c *gin.Context) {
	file, _, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   "No file provided",
		})
		return
	}
	defer file.Close()

	repayments, err := h.parseRepaymentCSV(file)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to parse CSV: %v", err),
		})
		return
	}

	count, err := h.insertRepayments(c.Request.Context(), repayments)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.UploadResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to insert repayments: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.UploadResponse{
		Success: true,
		Message: "Repayments uploaded successfully",
		Count:   count,
	})
}

// CSV parsing methods

func (h *UploadHandler) parseTransactionCSV(file io.Reader) ([]models.Transaction, error) {
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	if len(records) < 2 {
		return nil, fmt.Errorf("CSV must have at least a header and one data row")
	}

	// Validate headers
	expectedHeaders := []string{"txn_id", "user_id", "amount", "timestamp", "type", "payment_method", "items", "account_balance"}
	headers := records[0]
	if len(headers) != len(expectedHeaders) {
		return nil, fmt.Errorf("invalid headers, expected: %v", expectedHeaders)
	}

	var transactions []models.Transaction
	for i, record := range records[1:] {
		if len(record) != len(expectedHeaders) {
			return nil, fmt.Errorf("row %d has incorrect number of columns", i+2)
		}

		// Parse txn_id (generate UUID if not provided)
		var txnID uuid.UUID
		if record[0] == "" {
			txnID = uuid.New()
		} else {
			txnID, err = uuid.Parse(record[0])
			if err != nil {
				return nil, fmt.Errorf("row %d: invalid txn_id: %v", i+2, err)
			}
		}

		// Parse amount
		amount, err := strconv.ParseFloat(record[2], 64)
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid amount: %v", i+2, err)
		}

		// Parse timestamp
		timestamp, err := time.Parse(time.RFC3339, record[3])
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid timestamp: %v", i+2, err)
		}

		// Parse account balance
		accountBalance, err := strconv.ParseFloat(record[7], 64)
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid account_balance: %v", i+2, err)
		}

		// Validate type
		if record[4] != "credit" && record[4] != "debit" {
			return nil, fmt.Errorf("row %d: invalid type, must be 'credit' or 'debit'", i+2)
		}

		// Validate JSON in items field
		var itemsJSON interface{}
		if record[6] != "" {
			if err := json.Unmarshal([]byte(record[6]), &itemsJSON); err != nil {
				return nil, fmt.Errorf("row %d: invalid items JSON: %v", i+2, err)
			}
		}

		transactions = append(transactions, models.Transaction{
			TxnID:          txnID,
			UserID:         record[1],
			Amount:         amount,
			Timestamp:      timestamp,
			Type:           record[4],
			PaymentMethod:  record[5],
			Items:          record[6],
			AccountBalance: accountBalance,
			CreatedAt:      time.Now(),
		})
	}

	return transactions, nil
}

func (h *UploadHandler) parseLoanRequestCSV(file io.Reader) ([]models.LoanRequest, error) {
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	if len(records) < 2 {
		return nil, fmt.Errorf("CSV must have at least a header and one data row")
	}

	expectedHeaders := []string{"loan_id", "user_id", "amount_requested", "purpose", "request_timestamp"}
	headers := records[0]
	if len(headers) != len(expectedHeaders) {
		return nil, fmt.Errorf("invalid headers, expected: %v", expectedHeaders)
	}

	var loans []models.LoanRequest
	for i, record := range records[1:] {
		if len(record) != len(expectedHeaders) {
			return nil, fmt.Errorf("row %d has incorrect number of columns", i+2)
		}

		var loanID uuid.UUID
		if record[0] == "" {
			loanID = uuid.New()
		} else {
			loanID, err = uuid.Parse(record[0])
			if err != nil {
				return nil, fmt.Errorf("row %d: invalid loan_id: %v", i+2, err)
			}
		}

		amount, err := strconv.ParseFloat(record[2], 64)
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid amount_requested: %v", i+2, err)
		}

		timestamp, err := time.Parse(time.RFC3339, record[4])
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid request_timestamp: %v", i+2, err)
		}

		loans = append(loans, models.LoanRequest{
			LoanID:           loanID,
			UserID:           record[1],
			AmountRequested:  amount,
			Purpose:          record[3],
			RequestTimestamp: timestamp,
			CreatedAt:        time.Now(),
		})
	}

	return loans, nil
}

func (h *UploadHandler) parseCreditHistoryCSV(file io.Reader) ([]models.CreditHistory, error) {
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	if len(records) < 2 {
		return nil, fmt.Errorf("CSV must have at least a header and one data row")
	}

	expectedHeaders := []string{"user_id", "credit_score", "past_loans", "defaults_count"}
	headers := records[0]
	if len(headers) != len(expectedHeaders) {
		return nil, fmt.Errorf("invalid headers, expected: %v", expectedHeaders)
	}

	var creditHistory []models.CreditHistory
	for i, record := range records[1:] {
		if len(record) != len(expectedHeaders) {
			return nil, fmt.Errorf("row %d has incorrect number of columns", i+2)
		}

		creditScore, err := strconv.Atoi(record[1])
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid credit_score: %v", i+2, err)
		}

		if creditScore < 300 || creditScore > 850 {
			return nil, fmt.Errorf("row %d: credit_score must be between 300 and 850", i+2)
		}

		// Validate JSON in past_loans field
		if record[2] != "" {
			var pastLoansJSON interface{}
			if err := json.Unmarshal([]byte(record[2]), &pastLoansJSON); err != nil {
				return nil, fmt.Errorf("row %d: invalid past_loans JSON: %v", i+2, err)
			}
		}

		defaultsCount, err := strconv.Atoi(record[3])
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid defaults_count: %v", i+2, err)
		}

		creditHistory = append(creditHistory, models.CreditHistory{
			UserID:        record[0],
			CreditScore:   creditScore,
			PastLoans:     record[2],
			DefaultsCount: defaultsCount,
			CreatedAt:     time.Now(),
			UpdatedAt:     time.Now(),
		})
	}

	return creditHistory, nil
}

func (h *UploadHandler) parseKYCCSV(file io.Reader) ([]models.KYC, error) {
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	if len(records) < 2 {
		return nil, fmt.Errorf("CSV must have at least a header and one data row")
	}

	expectedHeaders := []string{"user_id", "verified_status", "documents", "verification_timestamp"}
	headers := records[0]
	if len(headers) != len(expectedHeaders) {
		return nil, fmt.Errorf("invalid headers, expected: %v", expectedHeaders)
	}

	var kyc []models.KYC
	for i, record := range records[1:] {
		if len(record) != len(expectedHeaders) {
			return nil, fmt.Errorf("row %d has incorrect number of columns", i+2)
		}

		verifiedStatus, err := strconv.ParseBool(record[1])
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid verified_status: %v", i+2, err)
		}

		// Validate JSON in documents field
		if record[2] != "" {
			var documentsJSON interface{}
			if err := json.Unmarshal([]byte(record[2]), &documentsJSON); err != nil {
				return nil, fmt.Errorf("row %d: invalid documents JSON: %v", i+2, err)
			}
		}

		var verificationTimestamp *time.Time
		if record[3] != "" {
			timestamp, err := time.Parse(time.RFC3339, record[3])
			if err != nil {
				return nil, fmt.Errorf("row %d: invalid verification_timestamp: %v", i+2, err)
			}
			verificationTimestamp = &timestamp
		}

		kyc = append(kyc, models.KYC{
			UserID:                record[0],
			VerifiedStatus:        verifiedStatus,
			Documents:             record[2],
			VerificationTimestamp: verificationTimestamp,
			CreatedAt:             time.Now(),
			UpdatedAt:             time.Now(),
		})
	}

	return kyc, nil
}

func (h *UploadHandler) parseRepaymentCSV(file io.Reader) ([]models.Repayment, error) {
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	if len(records) < 2 {
		return nil, fmt.Errorf("CSV must have at least a header and one data row")
	}

	expectedHeaders := []string{"repayment_id", "user_id", "loan_id", "amount", "timestamp", "status"}
	headers := records[0]
	if len(headers) != len(expectedHeaders) {
		return nil, fmt.Errorf("invalid headers, expected: %v", expectedHeaders)
	}

	var repayments []models.Repayment
	for i, record := range records[1:] {
		if len(record) != len(expectedHeaders) {
			return nil, fmt.Errorf("row %d has incorrect number of columns", i+2)
		}

		var repaymentID uuid.UUID
		if record[0] == "" {
			repaymentID = uuid.New()
		} else {
			repaymentID, err = uuid.Parse(record[0])
			if err != nil {
				return nil, fmt.Errorf("row %d: invalid repayment_id: %v", i+2, err)
			}
		}

		loanID, err := uuid.Parse(record[2])
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid loan_id: %v", i+2, err)
		}

		amount, err := strconv.ParseFloat(record[3], 64)
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid amount: %v", i+2, err)
		}

		timestamp, err := time.Parse(time.RFC3339, record[4])
		if err != nil {
			return nil, fmt.Errorf("row %d: invalid timestamp: %v", i+2, err)
		}

		// Validate status
		validStatuses := []string{"paid", "late", "default"}
		if !hasString(validStatuses, record[5]) {
			return nil, fmt.Errorf("row %d: invalid status, must be one of: %v", i+2, validStatuses)
		}

		repayments = append(repayments, models.Repayment{
			RepaymentID: repaymentID,
			UserID:      record[1],
			LoanID:      loanID,
			Amount:      amount,
			Timestamp:   timestamp,
			Status:      record[5],
			CreatedAt:   time.Now(),
		})
	}

	return repayments, nil
}

// Database insertion methods
func (h *UploadHandler) insertTransactions(ctx context.Context, transactions []models.Transaction) (int, error) {
	return h.batchInsert(ctx, "transactions", transactions, func(tx pgx.Tx, batch interface{}) error {
		query := `
			INSERT INTO transactions (txn_id, user_id, amount, timestamp, type, payment_method, items, account_balance, created_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
			ON CONFLICT (txn_id) DO NOTHING
		`

		for _, txn := range batch.([]models.Transaction) {
			_, err := tx.Exec(ctx, query, txn.TxnID, txn.UserID, txn.Amount, txn.Timestamp,
				txn.Type, txn.PaymentMethod, txn.Items, txn.AccountBalance, txn.CreatedAt)
			if err != nil {
				return err
			}
		}
		return nil
	})
}

func (h *UploadHandler) insertLoanRequests(ctx context.Context, loans []models.LoanRequest) (int, error) {
	return h.batchInsert(ctx, "loan_requests", loans, func(tx pgx.Tx, batch interface{}) error {
		query := `
			INSERT INTO loan_requests (loan_id, user_id, amount_requested, purpose, request_timestamp, created_at)
			VALUES ($1, $2, $3, $4, $5, $6)
			ON CONFLICT (loan_id) DO NOTHING
		`

		for _, loan := range batch.([]models.LoanRequest) {
			_, err := tx.Exec(ctx, query, loan.LoanID, loan.UserID, loan.AmountRequested,
				loan.Purpose, loan.RequestTimestamp, loan.CreatedAt)
			if err != nil {
				return err
			}
		}
		return nil
	})
}
func (h *UploadHandler) insertCreditHistory(ctx context.Context, creditHistory []models.CreditHistory) (int, error) {
	return h.batchInsert(ctx, "credit_history", creditHistory, func(tx pgx.Tx, batch interface{}) error {
		query := `
			INSERT INTO credit_history (user_id, credit_score, past_loans, defaults_count, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6)
			ON CONFLICT (user_id) DO UPDATE SET
				credit_score = EXCLUDED.credit_score,
				past_loans = EXCLUDED.past_loans,
				defaults_count = EXCLUDED.defaults_count,
				updated_at = EXCLUDED.updated_at
		`

		for _, ch := range batch.([]models.CreditHistory) {
			_, err := tx.Exec(ctx, query, ch.UserID, ch.CreditScore, ch.PastLoans,
				ch.DefaultsCount, ch.CreatedAt, ch.UpdatedAt)
			if err != nil {
				return err
			}
		}
		return nil
	})
}

func (h *UploadHandler) insertKYC(ctx context.Context, kyc []models.KYC) (int, error) {
	return h.batchInsert(ctx, "kyc", kyc, func(tx pgx.Tx, batch interface{}) error {
		query := `
			INSERT INTO kyc (user_id, verified_status, documents, verification_timestamp, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6)
			ON CONFLICT (user_id) DO UPDATE SET
				verified_status = EXCLUDED.verified_status,
				documents = EXCLUDED.documents,
				verification_timestamp = EXCLUDED.verification_timestamp,
				updated_at = EXCLUDED.updated_at
		`

		for _, k := range batch.([]models.KYC) {
			_, err := tx.Exec(ctx, query, k.UserID, k.VerifiedStatus, k.Documents,
				k.VerificationTimestamp, k.CreatedAt, k.UpdatedAt)
			if err != nil {
				return err
			}
		}
		return nil
	})
}

func (h *UploadHandler) insertRepayments(ctx context.Context, repayments []models.Repayment) (int, error) {
	return h.batchInsert(ctx, "repayments", repayments, func(tx pgx.Tx, batch interface{}) error {
		query := `
			INSERT INTO repayments (repayment_id, user_id, loan_id, amount, timestamp, status, created_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7)
			ON CONFLICT (repayment_id) DO NOTHING
		`

		for _, repayment := range batch.([]models.Repayment) {
			_, err := tx.Exec(ctx, query, repayment.RepaymentID, repayment.UserID,
				repayment.LoanID, repayment.Amount, repayment.Timestamp, repayment.Status, repayment.CreatedAt)
			if err != nil {
				return err
			}
		}
		return nil
	})
}

// Generic batch insert helper
func (h *UploadHandler) batchInsert(ctx context.Context, tableName string, items interface{}, insertFunc func(pgx.Tx, interface{}) error) (int, error) {
	const batchSize = 100

	var count int
	err := h.db.Transaction(ctx, func(tx pgx.Tx) error {
		// This is a simplified version - in practice, you'd need to handle different types
		// For now, we'll just call the insert function with the full batch
		return insertFunc(tx, items)
	})

	if err != nil {
		return 0, err
	}

	// For simplicity, return the length of items
	// In a real implementation, you'd count actual inserted rows
	switch v := items.(type) {
	case []models.Transaction:
		count = len(v)
	case []models.LoanRequest:
		count = len(v)
	case []models.CreditHistory:
		count = len(v)
	case []models.KYC:
		count = len(v)
	case []models.Repayment:
		count = len(v)
	}

	return count, nil
}

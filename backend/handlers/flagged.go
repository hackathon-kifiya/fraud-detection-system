package handlers

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"fraud-detection-backend/db"
	"fraud-detection-backend/models"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// FlaggedHandler handles flagged items operations
type FlaggedHandler struct {
	db *db.DB
}

// NewFlaggedHandler creates a new flagged handler
func NewFlaggedHandler(database *db.DB) *FlaggedHandler {
	return &FlaggedHandler{db: database}
}

// GetFlaggedItems retrieves flagged items with optional filtering and pagination
func (h *FlaggedHandler) GetFlaggedItems(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Parse query parameters
	status := c.Query("status")
	itemType := c.Query("type")
	userID := c.Query("user_id")
	pageStr := c.DefaultQuery("page", "1")
	limitStr := c.DefaultQuery("limit", "50")
	sortBy := c.DefaultQuery("sort_by", "created_at")
	sortOrder := c.DefaultQuery("sort_order", "desc")

	// Parse pagination parameters
	page, err := strconv.Atoi(pageStr)
	if err != nil || page < 1 {
		page = 1
	}

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit < 1 || limit > 100 {
		limit = 50
	}

	offset := (page - 1) * limit

	// Validate sort parameters
	validSortFields := map[string]bool{
		"created_at": true,
		"score":      true,
		"type":       true,
		"user_id":    true,
	}
	if !validSortFields[sortBy] {
		sortBy = "created_at"
	}

	if sortOrder != "asc" && sortOrder != "desc" {
		sortOrder = "desc"
	}

	// Build query
	query := `
		SELECT id, type, ref_id, user_id, score, reasons, status, verified_at, created_at
		FROM flagged_items
		WHERE 1=1
	`
	args := []interface{}{}
	argIndex := 1

	if status != "" {
		query += fmt.Sprintf(" AND status = $%d", argIndex)
		args = append(args, status)
		argIndex++
	}

	if itemType != "" {
		query += fmt.Sprintf(" AND type = $%d", argIndex)
		args = append(args, itemType)
		argIndex++
	}

	if userID != "" {
		query += fmt.Sprintf(" AND user_id = $%d", argIndex)
		args = append(args, userID)
		argIndex++
	}

	query += fmt.Sprintf(" ORDER BY %s %s LIMIT $%d OFFSET $%d", sortBy, sortOrder, argIndex, argIndex+1)
	args = append(args, limit, offset)

	// Execute query
	rows, err := h.db.Pool.Query(ctx, query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.FlaggedItemsResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to query flagged items: %v", err),
		})
		return
	}
	defer rows.Close()

	var items []models.FlaggedItem
	for rows.Next() {
		var item models.FlaggedItem
		var reasonsStr string
		var verifiedAt *time.Time

		err := rows.Scan(
			&item.ID,
			&item.Type,
			&item.RefID,
			&item.UserID,
			&item.Score,
			&reasonsStr,
			&item.Status,
			&verifiedAt,
			&item.CreatedAt,
		)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.FlaggedItemsResponse{
				Success: false,
				Error:   fmt.Sprintf("Failed to scan flagged item: %v", err),
			})
			return
		}

		item.Reasons = reasonsStr
		if verifiedAt != nil {
			item.VerifiedAt = verifiedAt
		}

		items = append(items, item)
	}

	// Get total count for pagination
	countQuery := "SELECT COUNT(*) FROM flagged_items WHERE 1=1"
	countArgs := []interface{}{}
	countArgIndex := 1

	if status != "" {
		countQuery += fmt.Sprintf(" AND status = $%d", countArgIndex)
		countArgs = append(countArgs, status)
		countArgIndex++
	}

	if itemType != "" {
		countQuery += fmt.Sprintf(" AND type = $%d", countArgIndex)
		countArgs = append(countArgs, itemType)
		countArgIndex++
	}

	if userID != "" {
		countQuery += fmt.Sprintf(" AND user_id = $%d", countArgIndex)
		countArgs = append(countArgs, userID)
		countArgIndex++
	}

	var total int
	err = h.db.Pool.QueryRow(ctx, countQuery, countArgs...).Scan(&total)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.FlaggedItemsResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to get total count: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, models.FlaggedItemsResponse{
		Success: true,
		Items:   items,
		Total:   total,
	})
}

// GetFlaggedItem retrieves a specific flagged item by ID
func (h *FlaggedHandler) GetFlaggedItem(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Parse item ID from URL parameter
	itemIDStr := c.Param("id")
	itemID, err := uuid.Parse(itemIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "Invalid item ID format",
		})
		return
	}

	// Query the specific item
	query := `
		SELECT id, type, ref_id, user_id, score, reasons, status, verified_at, created_at
		FROM flagged_items
		WHERE id = $1
	`

	var item models.FlaggedItem
	var reasonsStr string
	var verifiedAt *time.Time

	err = h.db.Pool.QueryRow(ctx, query, itemID).Scan(
		&item.ID,
		&item.Type,
		&item.RefID,
		&item.UserID,
		&item.Score,
		&reasonsStr,
		&item.Status,
		&verifiedAt,
		&item.CreatedAt,
	)

	if err != nil {
		if err.Error() == "no rows in result set" {
			c.JSON(http.StatusNotFound, gin.H{
				"success": false,
				"error":   "Flagged item not found",
			})
			return
		}

		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to query flagged item: %v", err),
		})
		return
	}

	item.Reasons = reasonsStr
	if verifiedAt != nil {
		item.VerifiedAt = verifiedAt
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"item":    item,
	})
}

// VerifyFlaggedItem updates the status of a flagged item
func (h *FlaggedHandler) VerifyFlaggedItem(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Parse item ID from URL parameter
	itemIDStr := c.Param("id")
	itemID, err := uuid.Parse(itemIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.VerifyResponse{
			Success: false,
			Error:   "Invalid item ID format",
		})
		return
	}

	// Parse request body
	var request models.VerifyRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, models.VerifyResponse{
			Success: false,
			Error:   fmt.Sprintf("Invalid request body: %v", err),
		})
		return
	}

	// Validate status
	validStatuses := []string{"fraud", "safe"}
	if !hasString(validStatuses, request.Status) {
		c.JSON(http.StatusBadRequest, models.VerifyResponse{
			Success: false,
			Error:   "Invalid status. Must be 'fraud' or 'safe'",
		})
		return
	}

	// Update the item status
	query := `
		UPDATE flagged_items 
		SET status = $1, verified_at = NOW()
		WHERE id = $2
	`

	result, err := h.db.Pool.Exec(ctx, query, request.Status, itemID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.VerifyResponse{
			Success: false,
			Error:   fmt.Sprintf("Failed to update flagged item: %v", err),
		})
		return
	}

	rowsAffected := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, models.VerifyResponse{
			Success: false,
			Error:   "Flagged item not found",
		})
		return
	}

	c.JSON(http.StatusOK, models.VerifyResponse{
		Success: true,
		Message: fmt.Sprintf("Flagged item marked as %s", request.Status),
	})
}

// GetFlaggedStats returns statistics about flagged items
func (h *FlaggedHandler) GetFlaggedStats(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	stats := make(map[string]interface{})

	// Get total counts by status
	var total, pending, fraud, safe int
	err := h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items").Scan(&total)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to get total count: %v", err),
		})
		return
	}

	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE status = 'pending'").Scan(&pending)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to get pending count: %v", err),
		})
		return
	}

	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE status = 'fraud'").Scan(&fraud)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to get fraud count: %v", err),
		})
		return
	}

	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE status = 'safe'").Scan(&safe)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to get safe count: %v", err),
		})
		return
	}

	stats["total"] = total
	stats["by_status"] = map[string]int{
		"pending": pending,
		"fraud":   fraud,
		"safe":    safe,
	}

	// Get counts by type
	rows, err := h.db.Pool.Query(ctx, "SELECT type, COUNT(*) FROM flagged_items GROUP BY type")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to get type counts: %v", err),
		})
		return
	}
	defer rows.Close()

	byType := make(map[string]int)
	for rows.Next() {
		var itemType string
		var count int
		if err := rows.Scan(&itemType, &count); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"success": false,
				"error":   fmt.Sprintf("Failed to scan type count: %v", err),
			})
			return
		}
		byType[itemType] = count
	}
	stats["by_type"] = byType

	// Get high-risk count (score >= 85)
	var highRisk int
	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE score >= 85").Scan(&highRisk)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to get high risk count: %v", err),
		})
		return
	}
	stats["high_risk"] = highRisk

	// Get recent activity (last 24 hours)
	var recent int
	err = h.db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM flagged_items WHERE created_at > NOW() - INTERVAL '24 hours'").Scan(&recent)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   fmt.Sprintf("Failed to get recent count: %v", err),
		})
		return
	}
	stats["recent_24h"] = recent

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"stats":   stats,
	})
}

// Helper function
func hasString(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

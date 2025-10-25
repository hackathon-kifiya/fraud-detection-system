package service

import (
	"context"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

type AuditService struct {
	flaggedItemRepo port.FlaggedItemRepository
	auditNoteRepo   port.AuditNoteRepository
	auditLogRepo    port.AuditLogRepository
}

// NewAuditService creates a new audit service
func NewAuditService(flaggedItemRepo port.FlaggedItemRepository, auditNoteRepo port.AuditNoteRepository, auditLogRepo port.AuditLogRepository) *AuditService {
	return &AuditService{
		flaggedItemRepo: flaggedItemRepo,
		auditNoteRepo:   auditNoteRepo,
		auditLogRepo:    auditLogRepo,
	}
}

// GetFlaggedItemDetail retrieves a flagged item with original data and all scores
func (s *AuditService) GetFlaggedItemDetail(ctx context.Context, id string) (*domain.FlaggedItemDetail, error) {
	// Get the flagged item
	item, err := s.flaggedItemRepo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get flagged item: %w", err)
	}

	// Get original data
	_, originalData, err := s.flaggedItemRepo.GetWithOriginalData(ctx, id, item.Type)
	if err != nil {
		return nil, fmt.Errorf("failed to get original data: %w", err)
	}

	// Get audit notes
	notes, err := s.auditNoteRepo.GetByFlaggedItemID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get audit notes: %w", err)
	}

	// Get audit trail
	auditTrail, err := s.auditLogRepo.GetByFlaggedItemID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get audit trail: %w", err)
	}

	// Parse score breakdown from details field
	// TODO: Implement proper JSON parsing of details field to extract individual scores
	// For now, we'll use the risk score as a placeholder
	ruleEngineScore := item.RuleEngineScore
	mlScore := item.MLScore
	anomalyScore := item.AnomalyScore

	detail := &domain.FlaggedItemDetail{
		FlaggedItem:     *item,
		OriginalData:    originalData,
		RuleEngineScore: ruleEngineScore,
		MLScore:         mlScore,
		AnomalyScore:    anomalyScore,
		AuditNotes:      notes,
		AuditTrail:      auditTrail,
	}

	return detail, nil
}

// ClassifyFlaggedItem classifies a flagged item as confirmed fraud or false positive
func (s *AuditService) ClassifyFlaggedItem(ctx context.Context, id, classification, userID, notes string) error {
	// Validate classification
	if classification != domain.StatusConfirmed && classification != domain.StatusFalsePositive {
		return fmt.Errorf("invalid classification: %s", classification)
	}

	// Get current item to check status
	item, err := s.flaggedItemRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get flagged item: %w", err)
	}

	oldStatus := item.Status

	// Update classification
	err = s.flaggedItemRepo.UpdateClassification(ctx, id, classification, userID, notes)
	if err != nil {
		return fmt.Errorf("failed to update classification: %w", err)
	}

	// Create audit log entry
	auditLog := &domain.AuditLog{
		FlaggedItemID: id,
		UserID:        userID,
		Action:        domain.ActionClassification,
		OldStatus:     &oldStatus,
		NewStatus:     &classification,
		Metadata:      fmt.Sprintf(`{"notes": "%s"}`, notes),
		Timestamp:     time.Now(),
	}

	err = s.auditLogRepo.Create(ctx, auditLog)
	if err != nil {
		// Log error but don't fail the operation
		fmt.Printf("Warning: failed to create audit log: %v\n", err)
	}

	return nil
}

// AddAuditNote adds a contextual note to a flagged item
func (s *AuditService) AddAuditNote(ctx context.Context, flaggedItemID, userID, noteText string) (*domain.AuditNote, error) {
	// Verify flagged item exists
	_, err := s.flaggedItemRepo.GetByID(ctx, flaggedItemID)
	if err != nil {
		return nil, fmt.Errorf("flagged item not found: %w", err)
	}

	// Create audit note
	note := &domain.AuditNote{
		FlaggedItemID: flaggedItemID,
		UserID:        userID,
		NoteText:      noteText,
		CreatedAt:     time.Now(),
	}

	err = s.auditNoteRepo.Create(ctx, note)
	if err != nil {
		return nil, fmt.Errorf("failed to create audit note: %w", err)
	}

	// Create audit log entry
	auditLog := &domain.AuditLog{
		FlaggedItemID: flaggedItemID,
		UserID:        userID,
		Action:        domain.ActionNoteAdded,
		Metadata:      fmt.Sprintf(`{"note_text": "%s"}`, noteText),
		Timestamp:     time.Now(),
	}

	err = s.auditLogRepo.Create(ctx, auditLog)
	if err != nil {
		// Log error but don't fail the operation
		fmt.Printf("Warning: failed to create audit log: %v\n", err)
	}

	return note, nil
}

// GetPersonalReviewHistory retrieves the auditor's review history
func (s *AuditService) GetPersonalReviewHistory(ctx context.Context, userID string, req domain.PersonalReviewHistoryRequest) (*domain.PersonalReviewHistoryResponse, error) {
	// Get reviewed items
	items, total, err := s.flaggedItemRepo.GetByReviewedBy(ctx, userID, req.Limit, req.Offset)
	if err != nil {
		return nil, fmt.Errorf("failed to get reviewed items: %w", err)
	}

	// Apply additional filters if needed
	filteredItems := items
	if req.Status != "" {
		var filtered []domain.FlaggedItem
		for _, item := range items {
			if item.Status == req.Status {
				filtered = append(filtered, item)
			}
		}
		filteredItems = filtered
	}

	if req.Type != "" {
		var filtered []domain.FlaggedItem
		for _, item := range filteredItems {
			if item.Type == req.Type {
				filtered = append(filtered, item)
			}
		}
		filteredItems = filtered
	}

	// Get statistics
	stats, err := s.auditLogRepo.GetStats(ctx, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get audit stats: %w", err)
	}

	response := &domain.PersonalReviewHistoryResponse{
		Items:  filteredItems,
		Total:  total,
		Limit:  req.Limit,
		Offset: req.Offset,
		Stats: struct {
			TotalReviewed     int64 `json:"total_reviewed"`
			ConfirmedFraud    int64 `json:"confirmed_fraud"`
			FalsePositives    int64 `json:"false_positives"`
			AverageReviewTime int64 `json:"average_review_time_minutes"`
		}{
			TotalReviewed:     stats.TotalReviewed,
			ConfirmedFraud:    stats.ConfirmedFraud,
			FalsePositives:    stats.FalsePositives,
			AverageReviewTime: stats.AverageReviewTime,
		},
	}

	return response, nil
}

// GetAuditTrail retrieves the complete audit trail for a flagged item
func (s *AuditService) GetAuditTrail(ctx context.Context, flaggedItemID string) ([]domain.AuditLog, error) {
	trail, err := s.auditLogRepo.GetByFlaggedItemID(ctx, flaggedItemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get audit trail: %w", err)
	}
	return trail, nil
}

// GetAuditStats retrieves auditor-specific statistics
func (s *AuditService) GetAuditStats(ctx context.Context, userID string) (*domain.AuditStats, error) {
	stats, err := s.auditLogRepo.GetStats(ctx, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get audit stats: %w", err)
	}
	return stats, nil
}

// ListFlaggedItemsForReview retrieves flagged items for auditor review with filters
func (s *AuditService) ListFlaggedItemsForReview(ctx context.Context, req domain.FlaggedItemListRequest) (*domain.FlaggedItemListResponse, error) {
	// Set defaults
	if req.Limit <= 0 {
		req.Limit = 10
	}
	if req.Offset < 0 {
		req.Offset = 0
	}

	// Get items from repository
	items, total, err := s.flaggedItemRepo.List(ctx, req.Limit, req.Offset, req.Type, req.Status)
	if err != nil {
		return nil, fmt.Errorf("failed to list flagged items: %w", err)
	}

	// Apply additional filters
	filteredItems := items
	if req.RiskScoreMin != nil || req.RiskScoreMax != nil {
		var filtered []domain.FlaggedItem
		for _, item := range items {
			if req.RiskScoreMin != nil && item.RiskScore < *req.RiskScoreMin {
				continue
			}
			if req.RiskScoreMax != nil && item.RiskScore > *req.RiskScoreMax {
				continue
			}
			filtered = append(filtered, item)
		}
		filteredItems = filtered
	}

	// Apply sorting
	// TODO: Implement proper sorting based on req.SortBy and req.SortOrder

	response := &domain.FlaggedItemListResponse{
		Items:  filteredItems,
		Total:  total,
		Limit:  req.Limit,
		Offset: req.Offset,
	}

	return response, nil
}

package service

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

type AuditService struct {
	flaggedItemRepo    port.FlaggedItemRepository
	auditNoteRepo      port.AuditNoteRepository
	auditLogRepo       port.AuditLogRepository
	caseAssignmentRepo port.CaseAssignmentRepository
	labeledDataRepo    port.LabeledDataRepository
	callbackRepo       port.CallbackRepository
}

// NewAuditService creates a new audit service
func NewAuditService(flaggedItemRepo port.FlaggedItemRepository, auditNoteRepo port.AuditNoteRepository, auditLogRepo port.AuditLogRepository, caseAssignmentRepo port.CaseAssignmentRepository, labeledDataRepo port.LabeledDataRepository, callbackRepo port.CallbackRepository) *AuditService {
	return &AuditService{
		flaggedItemRepo:    flaggedItemRepo,
		auditNoteRepo:      auditNoteRepo,
		auditLogRepo:       auditLogRepo,
		caseAssignmentRepo: caseAssignmentRepo,
		labeledDataRepo:    labeledDataRepo,
		callbackRepo:       callbackRepo,
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

	// Parse decision breakdown if available
	var breakdown *domain.DecisionBreakdown
	if item.DecisionBreakdown != "" {
		var b domain.DecisionBreakdown
		if err := json.Unmarshal([]byte(item.DecisionBreakdown), &b); err == nil {
			breakdown = &b
		}
	}

	// Get scores - they are already in the embedded FlaggedItem
	// The embedded fields will be flattened in JSON response
	detail := &domain.FlaggedItemDetail{
		FlaggedItem:  *item,
		OriginalData: originalData,
		Breakdown:    breakdown,
		AuditNotes:   notes,
		AuditTrail:   auditTrail,
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

	// Store labeled data for retraining
	s.storeLabeledDataAsync(ctx, item, classification, userID)

	// Invoke callback with decision
	s.invokeCallbackForDecision(ctx, item, classification)

	return nil
}

// storeLabeledDataAsync stores labeled data asynchronously for retraining
func (s *AuditService) storeLabeledDataAsync(ctx context.Context, item *domain.FlaggedItem, decision, labeledBy string) {
	go func() {
		// Get original facts from details or construct from item
		facts := map[string]interface{}{
			"data_id": item.DataID,
			"type":    item.Type,
		}

		labeledData := &domain.LabeledData{
			EntityID:      item.DataID,
			DataType:      item.Type,
			Facts:         facts,
			Decision:      decision,
			LabeledBy:     labeledBy,
			FlaggedItemID: item.ID,
		}

		if err := s.labeledDataRepo.Create(ctx, labeledData); err != nil {
			fmt.Printf("Warning: failed to store labeled data: %v\n", err)
		}
	}()
}

// invokeCallbackForDecision invokes callbacks with the final decision
func (s *AuditService) invokeCallbackForDecision(ctx context.Context, item *domain.FlaggedItem, decision string) {
	go func() {
		payload := map[string]interface{}{
			"entity_id":       item.DataID,
			"data_type":       item.Type,
			"flagged_item_id": item.ID,
			"decision":        decision,
			"decision_details": map[string]interface{}{
				"rule_engine_score": item.RuleEngineScore,
				"anomaly_score":     item.AnomalyScore,
				"ml_score":          item.MLScore,
				"risk_score":        item.RiskScore,
			},
			"timestamp": time.Now().Format(time.RFC3339),
		}

		if err := s.callbackRepo.SendCallback(ctx, item.Type, payload); err != nil {
			fmt.Printf("Warning: failed to send callback for classification: %v\n", err)
		}
	}()
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

// GetMyAssignments retrieves assignments for the logged-in auditor
func (s *AuditService) GetMyAssignments(ctx context.Context, auditorID string, limit, offset int, status string) ([]domain.CaseAssignment, int64, error) {
	return s.caseAssignmentRepo.GetByAuditorID(ctx, auditorID, limit, offset, status)
}

// GetAssignmentDetail retrieves assignment details for an auditor
func (s *AuditService) GetAssignmentDetail(ctx context.Context, assignmentID, auditorID string) (*domain.CaseAssignment, error) {
	assignment, err := s.caseAssignmentRepo.GetByID(ctx, assignmentID)
	if err != nil {
		return nil, fmt.Errorf("assignment not found: %w", err)
	}

	// Verify the assignment belongs to the auditor
	if assignment.AuditorID != auditorID {
		return nil, fmt.Errorf("assignment does not belong to this auditor")
	}

	return assignment, nil
}

// UpdateAssignmentStatus updates the status of an assignment
func (s *AuditService) UpdateAssignmentStatus(ctx context.Context, assignmentID, auditorID, status string) (*domain.CaseAssignment, error) {
	// Get existing assignment
	assignment, err := s.caseAssignmentRepo.GetByID(ctx, assignmentID)
	if err != nil {
		return nil, fmt.Errorf("assignment not found: %w", err)
	}

	// Verify the assignment belongs to the auditor
	if assignment.AuditorID != auditorID {
		return nil, fmt.Errorf("assignment does not belong to this auditor")
	}

	// Validate status transition
	oldStatus := assignment.Status
	if !isValidStatusTransition(oldStatus, status) {
		return nil, fmt.Errorf("invalid status transition from %s to %s", oldStatus, status)
	}

	// Update status
	assignment.Status = status
	err = s.caseAssignmentRepo.Update(ctx, assignment)
	if err != nil {
		return nil, fmt.Errorf("failed to update assignment status: %w", err)
	}

	// Create audit log entry
	auditLog := &domain.AuditLog{
		FlaggedItemID: assignment.FlaggedItemID,
		UserID:        auditorID,
		Action:        domain.ActionStatusChange,
		OldStatus:     &oldStatus,
		NewStatus:     &status,
		Metadata:      fmt.Sprintf(`{"assignment_id": "%s", "updated_by": "auditor"}`, assignment.ID),
	}
	s.auditLogRepo.Create(ctx, auditLog)

	return assignment, nil
}

// isValidStatusTransition validates if a status transition is allowed
func isValidStatusTransition(oldStatus, newStatus string) bool {
	validTransitions := map[string][]string{
		domain.AssignmentStatusAssigned:   {domain.AssignmentStatusInProgress, domain.AssignmentStatusCancelled},
		domain.AssignmentStatusInProgress: {domain.AssignmentStatusCompleted, domain.AssignmentStatusCancelled},
		domain.AssignmentStatusCompleted:  {}, // No transitions from completed
		domain.AssignmentStatusCancelled:  {}, // No transitions from cancelled
	}

	allowedTransitions, exists := validTransitions[oldStatus]
	if !exists {
		return false
	}

	for _, allowed := range allowedTransitions {
		if allowed == newStatus {
			return true
		}
	}
	return false
}

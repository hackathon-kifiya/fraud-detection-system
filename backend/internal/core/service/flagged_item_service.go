package service

import (
	"context"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
)

type FlaggedItemService struct {
	repo port.FlaggedItemRepository
}

// NewFlaggedItemService creates a new flagged item service
func NewFlaggedItemService(repo port.FlaggedItemRepository) *FlaggedItemService {
	return &FlaggedItemService{repo: repo}
}

// CreateFlaggedItem creates a new flagged item
func (s *FlaggedItemService) CreateFlaggedItem(ctx context.Context, req domain.CreateFlaggedItemRequest) (*domain.FlaggedItem, error) {
	item := &domain.FlaggedItem{
		Type:      req.Type,
		DataID:    req.DataID,
		Reason:    req.Reason,
		RiskScore: req.RiskScore,
		Status:    domain.StatusPending,
		Details:   req.Details,
		FlaggedBy: req.FlaggedBy,
	}

	if err := s.repo.Create(ctx, item); err != nil {
		return nil, fmt.Errorf("failed to create flagged item: %w", err)
	}

	return item, nil
}

// GetFlaggedItem retrieves a flagged item by ID
func (s *FlaggedItemService) GetFlaggedItem(ctx context.Context, id string) (*domain.FlaggedItem, error) {
	item, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get flagged item: %w", err)
	}
	return item, nil
}

// ListFlaggedItems retrieves flagged items with pagination and filters
func (s *FlaggedItemService) ListFlaggedItems(ctx context.Context, limit, offset int, itemType, status string) (*domain.FlaggedItemListResponse, error) {
	items, total, err := s.repo.List(ctx, limit, offset, itemType, status)
	if err != nil {
		return nil, fmt.Errorf("failed to list flagged items: %w", err)
	}

	return &domain.FlaggedItemListResponse{
		Items:  items,
		Total:  total,
		Limit:  limit,
		Offset: offset,
	}, nil
}

// UpdateFlaggedItem updates a flagged item
func (s *FlaggedItemService) UpdateFlaggedItem(ctx context.Context, id string, req domain.UpdateFlaggedItemRequest) (*domain.FlaggedItem, error) {
	item, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get flagged item: %w", err)
	}

	// Update fields
	item.Status = req.Status
	if req.ReviewedBy != nil {
		item.ReviewedBy = req.ReviewedBy
	}
	if req.Details != nil {
		item.Details = *req.Details
	}

	if err := s.repo.Update(ctx, item); err != nil {
		return nil, fmt.Errorf("failed to update flagged item: %w", err)
	}

	return item, nil
}

// DeleteFlaggedItem deletes a flagged item
func (s *FlaggedItemService) DeleteFlaggedItem(ctx context.Context, id string) error {
	if err := s.repo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete flagged item: %w", err)
	}
	return nil
}

// GetStats retrieves statistics about flagged items
func (s *FlaggedItemService) GetStats(ctx context.Context) (*domain.FlaggedItemStats, error) {
	stats, err := s.repo.GetStats(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get flagged item stats: %w", err)
	}
	return stats, nil
}

// GetFlaggedItemsByType retrieves flagged items by type
func (s *FlaggedItemService) GetFlaggedItemsByType(ctx context.Context, itemType string, limit, offset int) (*domain.FlaggedItemListResponse, error) {
	items, total, err := s.repo.GetByType(ctx, itemType, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to get flagged items by type: %w", err)
	}

	return &domain.FlaggedItemListResponse{
		Items:  items,
		Total:  total,
		Limit:  limit,
		Offset: offset,
	}, nil
}

// UpdateStatus updates the status of a flagged item
func (s *FlaggedItemService) UpdateStatus(ctx context.Context, id, status, reviewedBy string) error {
	if err := s.repo.UpdateStatus(ctx, id, status, reviewedBy); err != nil {
		return fmt.Errorf("failed to update flagged item status: %w", err)
	}
	return nil
}

// VerifyFlaggedItem verifies a flagged item (marks as confirmed or false positive)
func (s *FlaggedItemService) VerifyFlaggedItem(ctx context.Context, id, status, reviewedBy string) error {
	validStatuses := []string{domain.StatusConfirmed, domain.StatusFalsePositive, domain.StatusReviewed}

	valid := false
	for _, validStatus := range validStatuses {
		if status == validStatus {
			valid = true
			break
		}
	}

	if !valid {
		return fmt.Errorf("invalid status: %s", status)
	}

	if err := s.UpdateStatus(ctx, id, status, reviewedBy); err != nil {
		return fmt.Errorf("failed to verify flagged item: %w", err)
	}

	return nil
}

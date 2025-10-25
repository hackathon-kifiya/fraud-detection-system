package repository

import (
	"context"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

type CaseAssignmentRepository struct {
	db *gorm.DB
}

// NewCaseAssignmentRepository creates a new case assignment repository
func NewCaseAssignmentRepository(db *gorm.DB) port.CaseAssignmentRepository {
	return &CaseAssignmentRepository{db: db}
}

// Create creates a new case assignment
func (r *CaseAssignmentRepository) Create(ctx context.Context, assignment *domain.CaseAssignment) error {
	result := r.db.WithContext(ctx).Create(assignment)
	if result.Error != nil {
		return fmt.Errorf("failed to create case assignment: %w", result.Error)
	}
	return nil
}

// GetByID retrieves a case assignment by ID
func (r *CaseAssignmentRepository) GetByID(ctx context.Context, id string) (*domain.CaseAssignment, error) {
	var assignment domain.CaseAssignment
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&assignment)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("case assignment not found")
		}
		return nil, fmt.Errorf("failed to get case assignment: %w", result.Error)
	}
	return &assignment, nil
}

// GetByFlaggedItemID retrieves assignment for a flagged item
func (r *CaseAssignmentRepository) GetByFlaggedItemID(ctx context.Context, flaggedItemID string) (*domain.CaseAssignment, error) {
	var assignment domain.CaseAssignment
	result := r.db.WithContext(ctx).Where("flagged_item_id = ?", flaggedItemID).First(&assignment)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("case assignment not found")
		}
		return nil, fmt.Errorf("failed to get case assignment: %w", result.Error)
	}
	return &assignment, nil
}

// GetByAuditorID retrieves assignments for an auditor
func (r *CaseAssignmentRepository) GetByAuditorID(ctx context.Context, auditorID string, limit, offset int) ([]domain.CaseAssignment, int64, error) {
	var assignments []domain.CaseAssignment
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.CaseAssignment{}).Where("auditor_id = ?", auditorID)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count case assignments: %w", err)
	}

	// Get items with pagination
	result := query.Order("assigned_at DESC").Limit(limit).Offset(offset).Find(&assignments)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to get case assignments: %w", result.Error)
	}

	return assignments, total, nil
}

// List retrieves case assignments with pagination and filters
func (r *CaseAssignmentRepository) List(ctx context.Context, limit, offset int, status, priority string) ([]domain.CaseAssignment, int64, error) {
	var assignments []domain.CaseAssignment
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.CaseAssignment{})

	// Apply filters
	if status != "" {
		query = query.Where("status = ?", status)
	}
	if priority != "" {
		query = query.Where("priority = ?", priority)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count case assignments: %w", err)
	}

	// Get items with pagination
	result := query.Order("assigned_at DESC").Limit(limit).Offset(offset).Find(&assignments)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to list case assignments: %w", result.Error)
	}

	return assignments, total, nil
}

// Update updates a case assignment
func (r *CaseAssignmentRepository) Update(ctx context.Context, assignment *domain.CaseAssignment) error {
	result := r.db.WithContext(ctx).Save(assignment)
	if result.Error != nil {
		return fmt.Errorf("failed to update case assignment: %w", result.Error)
	}
	return nil
}

// Delete deletes a case assignment
func (r *CaseAssignmentRepository) Delete(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Delete(&domain.CaseAssignment{}, "id = ?", id)
	if result.Error != nil {
		return fmt.Errorf("failed to delete case assignment: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("case assignment not found")
	}
	return nil
}

// GetUnassignedCases retrieves flagged items without assignments
func (r *CaseAssignmentRepository) GetUnassignedCases(ctx context.Context, limit, offset int) ([]domain.FlaggedItem, int64, error) {
	var items []domain.FlaggedItem
	var total int64

	// Subquery to find flagged items that don't have assignments
	subQuery := r.db.WithContext(ctx).Model(&domain.CaseAssignment{}).Select("flagged_item_id")

	query := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("id NOT IN (?)", subQuery)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count unassigned cases: %w", err)
	}

	// Get items with pagination
	result := query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&items)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to get unassigned cases: %w", result.Error)
	}

	return items, total, nil
}

// GetAuditorWorkload retrieves workload distribution for all auditors
func (r *CaseAssignmentRepository) GetAuditorWorkload(ctx context.Context) ([]domain.AuditorWorkloadResponse, error) {
	var workloads []domain.AuditorWorkloadResponse

	// This is a complex query that would need to be implemented based on specific requirements
	// For now, return empty slice as placeholder
	// TODO: Implement actual workload calculation query

	return workloads, nil
}

// GetOverdueAssignments retrieves overdue assignments
func (r *CaseAssignmentRepository) GetOverdueAssignments(ctx context.Context) ([]domain.CaseAssignment, error) {
	var assignments []domain.CaseAssignment
	now := time.Now()

	result := r.db.WithContext(ctx).
		Where("due_date < ? AND status IN (?)", now, []string{domain.AssignmentStatusAssigned, domain.AssignmentStatusInProgress}).
		Order("due_date ASC").
		Find(&assignments)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to get overdue assignments: %w", result.Error)
	}

	return assignments, nil
}

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

// GetByAuditorID retrieves assignments for an auditor with optional status filter
func (r *CaseAssignmentRepository) GetByAuditorID(ctx context.Context, auditorID string, limit, offset int, status string) ([]domain.CaseAssignment, int64, error) {
	var assignments []domain.CaseAssignment
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.CaseAssignment{}).Where("auditor_id = ?", auditorID)

	// Apply status filter if provided
	if status != "" {
		query = query.Where("status = ?", status)
	}

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

	// Get all case assignments first
	var assignedItemIDs []string
	if err := r.db.WithContext(ctx).Model(&domain.CaseAssignment{}).Select("flagged_item_id").Find(&assignedItemIDs).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to get assigned cases: %w", err)
	}

	// Query flagged items that are pending and not in the assigned list
	query := r.db.WithContext(ctx).Model(&domain.FlaggedItem{}).Where("status = ?", "pending")

	if len(assignedItemIDs) > 0 {
		query = query.Where("id NOT IN ?", assignedItemIDs)
	}

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

	// Get all auditors (users with role 'analyst')
	var auditors []struct {
		ID        string `json:"id"`
		FirstName string `json:"first_name"`
		LastName  string `json:"last_name"`
		IsActive  bool   `json:"is_active"`
	}

	err := r.db.WithContext(ctx).
		Table("users").
		Select("id, first_name, last_name, is_active").
		Where("role = ? AND is_active = ?", "analyst", true).
		Find(&auditors).Error

	if err != nil {
		return nil, fmt.Errorf("failed to get auditors: %w", err)
	}

	// Calculate workload for each auditor
	for _, auditor := range auditors {
		workload := domain.AuditorWorkloadResponse{
			AuditorID:   auditor.ID,
			AuditorName: fmt.Sprintf("%s %s", auditor.FirstName, auditor.LastName),
			IsAvailable: auditor.IsActive,
		}

		// Count active assignments
		var activeCount int64
		err = r.db.WithContext(ctx).
			Model(&domain.CaseAssignment{}).
			Where("auditor_id = ? AND status IN (?)", auditor.ID, []string{domain.AssignmentStatusAssigned, domain.AssignmentStatusInProgress}).
			Count(&activeCount).Error
		if err != nil {
			return nil, fmt.Errorf("failed to count active assignments for auditor %s: %w", auditor.ID, err)
		}
		workload.ActiveAssignments = activeCount

		// Count completed assignments today
		today := time.Now().Truncate(24 * time.Hour)
		var completedToday int64
		err = r.db.WithContext(ctx).
			Model(&domain.CaseAssignment{}).
			Where("auditor_id = ? AND status = ? AND updated_at >= ?", auditor.ID, domain.AssignmentStatusCompleted, today).
			Count(&completedToday).Error
		if err != nil {
			return nil, fmt.Errorf("failed to count completed assignments today for auditor %s: %w", auditor.ID, err)
		}
		workload.CompletedToday = completedToday

		// Count completed assignments this week
		weekStart := time.Now().AddDate(0, 0, -int(time.Now().Weekday())).Truncate(24 * time.Hour)
		var completedThisWeek int64
		err = r.db.WithContext(ctx).
			Model(&domain.CaseAssignment{}).
			Where("auditor_id = ? AND status = ? AND updated_at >= ?", auditor.ID, domain.AssignmentStatusCompleted, weekStart).
			Count(&completedThisWeek).Error
		if err != nil {
			return nil, fmt.Errorf("failed to count completed assignments this week for auditor %s: %w", auditor.ID, err)
		}
		workload.CompletedThisWeek = completedThisWeek

		// Calculate average review time (simplified - using assignment duration)
		var avgReviewTime float64

		err = r.db.WithContext(ctx).
			Model(&domain.CaseAssignment{}).
			Select("AVG(EXTRACT(EPOCH FROM (updated_at - assigned_at))/60)").
			Where("auditor_id = ? AND status = ? AND updated_at > assigned_at", auditor.ID, domain.AssignmentStatusCompleted).
			Scan(&avgReviewTime).Error

		if err != nil {
			// If no completed assignments, set to 0
			avgReviewTime = 0
		}
		workload.AvgReviewTime = avgReviewTime

		// Calculate efficiency score (simplified: completed assignments per day)
		daysSinceStart := time.Since(time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC)).Hours() / 24
		if daysSinceStart > 0 {
			workload.Efficiency = float64(completedThisWeek) / 7.0 // assignments per day this week
		} else {
			workload.Efficiency = 0
		}

		workloads = append(workloads, workload)
	}

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

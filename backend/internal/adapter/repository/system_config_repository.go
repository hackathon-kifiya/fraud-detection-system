package repository

import (
	"context"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

type SystemConfigRepository struct {
	db *gorm.DB
}

// NewSystemConfigRepository creates a new system config repository
func NewSystemConfigRepository(db *gorm.DB) port.SystemConfigRepository {
	return &SystemConfigRepository{db: db}
}

// Create creates a new system configuration
func (r *SystemConfigRepository) Create(ctx context.Context, config *domain.SystemConfig) error {
	result := r.db.WithContext(ctx).Create(config)
	if result.Error != nil {
		return fmt.Errorf("failed to create system config: %w", result.Error)
	}
	return nil
}

// GetByKey retrieves a system configuration by key
func (r *SystemConfigRepository) GetByKey(ctx context.Context, key string) (*domain.SystemConfig, error) {
	var config domain.SystemConfig
	result := r.db.WithContext(ctx).Where("config_key = ?", key).First(&config)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("system config not found")
		}
		return nil, fmt.Errorf("failed to get system config: %w", result.Error)
	}
	return &config, nil
}

// GetAll retrieves all system configurations
func (r *SystemConfigRepository) GetAll(ctx context.Context) ([]domain.SystemConfig, error) {
	var configs []domain.SystemConfig
	result := r.db.WithContext(ctx).Order("config_key ASC").Find(&configs)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to get system configs: %w", result.Error)
	}
	return configs, nil
}

// Update updates a system configuration
func (r *SystemConfigRepository) Update(ctx context.Context, config *domain.SystemConfig) error {
	result := r.db.WithContext(ctx).Save(config)
	if result.Error != nil {
		return fmt.Errorf("failed to update system config: %w", result.Error)
	}
	return nil
}

// Delete deletes a system configuration
func (r *SystemConfigRepository) Delete(ctx context.Context, key string) error {
	result := r.db.WithContext(ctx).Delete(&domain.SystemConfig{}, "config_key = ?", key)
	if result.Error != nil {
		return fmt.Errorf("failed to delete system config: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("system config not found")
	}
	return nil
}

// GetByType retrieves configurations by type
func (r *SystemConfigRepository) GetByType(ctx context.Context, configType string) ([]domain.SystemConfig, error) {
	var configs []domain.SystemConfig
	result := r.db.WithContext(ctx).Where("config_type = ?", configType).Order("config_key ASC").Find(&configs)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to get system configs by type: %w", result.Error)
	}
	return configs, nil
}

// GetHistory retrieves configuration change history
func (r *SystemConfigRepository) GetHistory(ctx context.Context, key string, limit, offset int) ([]domain.SystemConfig, int64, error) {
	var configs []domain.SystemConfig
	var total int64

	query := r.db.WithContext(ctx).Model(&domain.SystemConfig{}).Where("config_key = ?", key)

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("failed to count system config history: %w", err)
	}

	// Get items with pagination
	result := query.Order("updated_at DESC").Limit(limit).Offset(offset).Find(&configs)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("failed to get system config history: %w", result.Error)
	}

	return configs, total, nil
}

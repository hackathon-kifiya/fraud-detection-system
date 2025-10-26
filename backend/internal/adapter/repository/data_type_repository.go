package repository

import (
	"context"
	"database/sql/driver"
	"encoding/json"
	"errors"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"gorm.io/gorm"
)

// DataTypeRepository implements port.DataTypeRepository
type DataTypeRepository struct {
	db *gorm.DB
}

// NewDataTypeRepository creates a new instance of DataTypeRepository
func NewDataTypeRepository(db *gorm.DB) port.DataTypeRepository {
	return &DataTypeRepository{db: db}
}

// JSONB is a custom type for handling JSONB in PostgreSQL
type JSONB map[string]interface{}

// Value implements the driver.Valuer interface
func (j JSONB) Value() (driver.Value, error) {
	if j == nil {
		return nil, nil
	}
	return json.Marshal(j)
}

// Scan implements the sql.Scanner interface
func (j *JSONB) Scan(value interface{}) error {
	if value == nil {
		*j = nil
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("failed to unmarshal JSONB value")
	}
	return json.Unmarshal(bytes, j)
}

// Create creates a new data type
func (r *DataTypeRepository) Create(ctx context.Context, dataType *domain.DataType) error {
	result := r.db.WithContext(ctx).Create(dataType)
	if result.Error != nil {
		return fmt.Errorf("failed to create data type: %w", result.Error)
	}
	return nil
}

// GetByID retrieves a data type by ID
func (r *DataTypeRepository) GetByID(ctx context.Context, id string) (*domain.DataType, error) {
	var dataType domain.DataType
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&dataType)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("data type not found")
		}
		return nil, fmt.Errorf("failed to get data type by ID: %w", result.Error)
	}
	return &dataType, nil
}

// GetByDataType retrieves a data type by data type name
func (r *DataTypeRepository) GetByDataType(ctx context.Context, dataType string) (*domain.DataType, error) {
	var dt domain.DataType
	result := r.db.WithContext(ctx).Where("data_type = ?", dataType).First(&dt)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("data type not found")
		}
		return nil, fmt.Errorf("failed to get data type: %w", result.Error)
	}
	return &dt, nil
}

// Exists checks if a data type exists
func (r *DataTypeRepository) Exists(ctx context.Context, dataType string) (bool, error) {
	var count int64
	result := r.db.WithContext(ctx).Model(&domain.DataType{}).Where("data_type = ?", dataType).Count(&count)
	if result.Error != nil {
		return false, fmt.Errorf("failed to check if data type exists: %w", result.Error)
	}
	return count > 0, nil
}

// Update updates a data type
func (r *DataTypeRepository) Update(ctx context.Context, dataType *domain.DataType) error {
	result := r.db.WithContext(ctx).Save(dataType)
	if result.Error != nil {
		return fmt.Errorf("failed to update data type: %w", result.Error)
	}
	return nil
}

// Delete deletes a data type by ID
func (r *DataTypeRepository) Delete(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Where("id = ?", id).Delete(&domain.DataType{})
	if result.Error != nil {
		return fmt.Errorf("failed to delete data type: %w", result.Error)
	}
	return nil
}

// List retrieves all data types with pagination
func (r *DataTypeRepository) List(ctx context.Context, limit, offset int) ([]domain.DataType, int64, error) {
	var dataTypes []domain.DataType

	// Get total count
	var total int64
	countResult := r.db.WithContext(ctx).Model(&domain.DataType{}).Count(&total)
	if countResult.Error != nil {
		return nil, 0, fmt.Errorf("failed to count data types: %w", countResult.Error)
	}

	// Get paginated results
	listResult := r.db.WithContext(ctx).
		Order("created_at DESC").
		Limit(limit).
		Offset(offset).
		Find(&dataTypes)

	if listResult.Error != nil {
		return nil, 0, fmt.Errorf("failed to list data types: %w", listResult.Error)
	}

	return dataTypes, total, nil
}

// Count returns the total number of data types
func (r *DataTypeRepository) Count(ctx context.Context) (int64, error) {
	var count int64
	result := r.db.WithContext(ctx).Model(&domain.DataType{}).Count(&count)
	if result.Error != nil {
		return 0, fmt.Errorf("failed to count data types: %w", result.Error)
	}
	return count, nil
}

// GetByStatus retrieves data types by status
func (r *DataTypeRepository) GetByStatus(ctx context.Context, status string) ([]domain.DataType, error) {
	var dataTypes []domain.DataType
	result := r.db.WithContext(ctx).Where("status = ?", status).Find(&dataTypes)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to get data types by status: %w", result.Error)
	}
	return dataTypes, nil
}

// GetActive retrieves all active data types
func (r *DataTypeRepository) GetActive(ctx context.Context) ([]domain.DataType, error) {
	return r.GetByStatus(ctx, domain.DataTypeStatusActive)
}

// Search searches data types by name, data_type, or description
func (r *DataTypeRepository) Search(ctx context.Context, query string) ([]domain.DataType, error) {
	var dataTypes []domain.DataType
	searchPattern := "%" + query + "%"
	result := r.db.WithContext(ctx).
		Where("data_type ILIKE ? OR name ILIKE ? OR description ILIKE ?", searchPattern, searchPattern, searchPattern).
		Find(&dataTypes)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to search data types: %w", result.Error)
	}
	return dataTypes, nil
}

// ExistsByDataTypeAndIDNot checks if a data type exists with a different ID
func (r *DataTypeRepository) ExistsByDataTypeAndIDNot(ctx context.Context, dataType string, id string) (bool, error) {
	var count int64
	result := r.db.WithContext(ctx).
		Model(&domain.DataType{}).
		Where("data_type = ? AND id != ?", dataType, id).
		Count(&count)
	if result.Error != nil {
		return false, fmt.Errorf("failed to check if data type exists: %w", result.Error)
	}
	return count > 0, nil
}

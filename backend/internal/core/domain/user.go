package domain

import (
	"time"
)

// User represents a user in the system
type User struct {
	ID        string    `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	Email     string    `json:"email" gorm:"uniqueIndex;not null"`
	Password  string    `json:"-" gorm:"column:password_hash;not null"` // Never expose password in JSON
	FirstName string    `json:"first_name" gorm:"column:first_name;not null"`
	LastName  string    `json:"last_name" gorm:"column:last_name;not null"`
	Role      string    `json:"role" gorm:"not null;default:'viewer'"`
	IsActive  bool      `json:"is_active" gorm:"column:is_active;default:true"`
	CreatedAt time.Time `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt time.Time `json:"updated_at" gorm:"autoUpdateTime"`
}

// TableName specifies the table name for GORM
func (User) TableName() string {
	return "users"
}

// UserRole constants
const (
	RoleAdmin     = "admin"
	RoleAnalyst   = "analyst"
	RoleViewer    = "viewer"
	RoleLabTechie = "lab_techie"
)

// CreateUserRequest represents the request to create a new user
type CreateUserRequest struct {
	Email     string `json:"email" binding:"required,email"`
	Password  string `json:"password" binding:"required,min=8"`
	FirstName string `json:"first_name" binding:"required"`
	LastName  string `json:"last_name" binding:"required"`
	Role      string `json:"role" binding:"required,oneof=admin analyst viewer lab_techie"`
}

// UpdateUserRequest represents the request to update a user
type UpdateUserRequest struct {
	FirstName *string `json:"first_name,omitempty"`
	LastName  *string `json:"last_name,omitempty"`
	Role      *string `json:"role,omitempty" binding:"oneof=admin analyst viewer lab_techie"`
	IsActive  *bool   `json:"is_active,omitempty"`
}

// LoginRequest represents the login credentials
type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
}

// LoginResponse represents the response after successful login
type LoginResponse struct {
	Token string `json:"token"`
	User  User   `json:"user"`
}

// ChangePasswordRequest represents the request to change password
type ChangePasswordRequest struct {
	OldPassword string `json:"old_password" binding:"required"`
	NewPassword string `json:"new_password" binding:"required,min=8"`
}

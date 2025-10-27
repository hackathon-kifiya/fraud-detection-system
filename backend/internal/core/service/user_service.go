package service

import (
	"context"
	"errors"
	"fmt"
	"time"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/port"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

var (
	ErrInvalidCredentials = errors.New("invalid credentials")
	ErrUserNotFound       = errors.New("user not found")
	ErrUserExists         = errors.New("user already exists")
	ErrUnauthorized       = errors.New("unauthorized")
)

// UserService handles business logic for user management
type UserService struct {
	userRepo  port.UserRepository
	jwtSecret string
}

// NewUserService creates a new instance of UserService
func NewUserService(userRepo port.UserRepository, jwtSecret string) *UserService {
	return &UserService{
		userRepo:  userRepo,
		jwtSecret: jwtSecret,
	}
}

// Register creates a new user
func (s *UserService) Register(ctx context.Context, req domain.CreateUserRequest) (*domain.User, error) {
	// Check if user already exists
	existingUser, _ := s.userRepo.GetByEmail(ctx, req.Email)
	if existingUser != nil {
		return nil, ErrUserExists
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, fmt.Errorf("failed to hash password: %w", err)
	}

	// Create user
	user := &domain.User{
		ID:        uuid.New().String(),
		Email:     req.Email,
		Password:  string(hashedPassword),
		FirstName: req.FirstName,
		LastName:  req.LastName,
		Role:      req.Role,
		IsActive:  true,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err = s.userRepo.Create(ctx, user)
	if err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	// Clear password before returning
	user.Password = ""
	return user, nil
}

// Login authenticates a user and returns a JWT token
func (s *UserService) Login(ctx context.Context, req domain.LoginRequest) (*domain.LoginResponse, error) {
	// Get user by email
	user, err := s.userRepo.GetByEmail(ctx, req.Email)
	if err != nil {
		return nil, ErrInvalidCredentials
	}

	// Check if user is active
	if !user.IsActive {
		return nil, ErrUnauthorized
	}

	// Verify password
	err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password))
	if err != nil {
		return nil, ErrInvalidCredentials
	}

	// Generate JWT token
	token, err := s.generateToken(user)
	if err != nil {
		return nil, fmt.Errorf("failed to generate token: %w", err)
	}

	// Clear password before returning
	user.Password = ""

	return &domain.LoginResponse{
		Token: token,
		User:  *user,
	}, nil
}

// GetUser retrieves a user by ID
func (s *UserService) GetUser(ctx context.Context, id string) (*domain.User, error) {
	user, err := s.userRepo.GetByID(ctx, id)
	if err != nil {
		return nil, ErrUserNotFound
	}

	// Clear password before returning
	user.Password = ""
	return user, nil
}

// UpdateUser updates a user's information
func (s *UserService) UpdateUser(ctx context.Context, id string, req domain.UpdateUserRequest) (*domain.User, error) {
	// Get existing user
	user, err := s.userRepo.GetByID(ctx, id)
	if err != nil {
		return nil, ErrUserNotFound
	}

	// Update fields if provided
	if req.FirstName != nil {
		user.FirstName = *req.FirstName
	}
	if req.LastName != nil {
		user.LastName = *req.LastName
	}
	if req.Role != nil {
		user.Role = *req.Role
	}
	if req.IsActive != nil {
		user.IsActive = *req.IsActive
	}

	user.UpdatedAt = time.Now()

	err = s.userRepo.Update(ctx, user)
	if err != nil {
		return nil, fmt.Errorf("failed to update user: %w", err)
	}

	// Clear password before returning
	user.Password = ""
	return user, nil
}

// DeleteUser deletes a user
func (s *UserService) DeleteUser(ctx context.Context, id string) error {
	err := s.userRepo.Delete(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to delete user: %w", err)
	}
	return nil
}

// ListUsers retrieves all users with pagination and optional role filter
func (s *UserService) ListUsers(ctx context.Context, limit, offset int, role string) ([]*domain.User, int64, error) {
	users, total, err := s.userRepo.List(ctx, limit, offset, role)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to list users: %w", err)
	}

	// Clear passwords
	for _, user := range users {
		user.Password = ""
	}

	return users, total, nil
}

// ChangePassword changes a user's password
func (s *UserService) ChangePassword(ctx context.Context, userID string, req domain.ChangePasswordRequest) error {
	// Get user
	user, err := s.userRepo.GetByID(ctx, userID)
	if err != nil {
		return ErrUserNotFound
	}

	// Verify old password
	err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.OldPassword))
	if err != nil {
		return ErrInvalidCredentials
	}

	// Hash new password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.NewPassword), bcrypt.DefaultCost)
	if err != nil {
		return fmt.Errorf("failed to hash password: %w", err)
	}

	// Update password
	user.Password = string(hashedPassword)
	user.UpdatedAt = time.Now()

	err = s.userRepo.Update(ctx, user)
	if err != nil {
		return fmt.Errorf("failed to update password: %w", err)
	}

	return nil
}

// generateToken generates a JWT token for a user
func (s *UserService) generateToken(user *domain.User) (string, error) {
	claims := jwt.MapClaims{
		"user_id": user.ID,
		"email":   user.Email,
		"role":    user.Role,
		"exp":     time.Now().Add(24 * time.Hour).Unix(),
		"iat":     time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(s.jwtSecret))
}

// ValidateToken validates a JWT token and returns the claims
func (s *UserService) ValidateToken(tokenString string) (jwt.MapClaims, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(s.jwtSecret), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, ErrUnauthorized
}

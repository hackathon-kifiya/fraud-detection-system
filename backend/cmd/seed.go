package main

import (
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/repository"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"gorm.io/gorm"
)

// seedDatabase populates the database with sample data
func seedDatabase(db *gorm.DB) error {
	userRepo := repository.NewUserRepository(db)
	userService := service.NewUserService(userRepo, "your-secret-key")

	// Create admin user
	adminUser := domain.CreateUserRequest{
		Email:     "admin@fraud-detection.com",
		Password:  "admin123",
		FirstName: "Admin",
		LastName:  "User",
		Role:      domain.RoleAdmin,
	}

	_, err := userService.Register(nil, adminUser)
	if err != nil && err != service.ErrUserExists {
		return fmt.Errorf("failed to create admin user: %w", err)
	}

	// Create analyst user
	analystUser := domain.CreateUserRequest{
		Email:     "analyst@fraud-detection.com",
		Password:  "analyst123",
		FirstName: "Analyst",
		LastName:  "User",
		Role:      domain.RoleAnalyst,
	}

	_, err = userService.Register(nil, analystUser)
	if err != nil && err != service.ErrUserExists {
		return fmt.Errorf("failed to create analyst user: %w", err)
	}

	// Create viewer user
	viewerUser := domain.CreateUserRequest{
		Email:     "viewer@fraud-detection.com",
		Password:  "viewer123",
		FirstName: "Viewer",
		LastName:  "User",
		Role:      domain.RoleViewer,
	}

	_, err = userService.Register(nil, viewerUser)
	if err != nil && err != service.ErrUserExists {
		return fmt.Errorf("failed to create viewer user: %w", err)
	}

	// Create lab techie user
	labTechieUser := domain.CreateUserRequest{
		Email:     "labtechie@fraud-detection.com",
		Password:  "labtechie123",
		FirstName: "Lab Techie",
		LastName:  "User",
		Role:      domain.RoleLabTechie,
	}

	_, err = userService.Register(nil, labTechieUser)
	if err != nil && err != service.ErrUserExists {
		return fmt.Errorf("failed to create lab techie user: %w", err)
	}

	return nil
}

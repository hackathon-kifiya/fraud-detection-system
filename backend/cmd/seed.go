package main

import (
	"context"
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

	_, err := userService.Register(context.TODO(), adminUser)
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

	_, err = userService.Register(context.TODO(), analystUser)
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

	_, err = userService.Register(context.TODO(), viewerUser)
	if err != nil && err != service.ErrUserExists {
		return fmt.Errorf("failed to create viewer user: %w", err)
	}

	// Data types are managed by the Data Management Service
	// They are seeded automatically when the Data Management Service starts
	fmt.Println("Data types are managed by the Data Management Service")
	fmt.Println("Please ensure the Data Management Service is running to have data types available")

	return nil
}

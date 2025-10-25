package main

import (
	"flag"
	"fmt"
	"log"

	"com.github.hackathon-kifiya.fraud-detection-system/config"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/database"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/repository"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"gorm.io/gorm"
)

// seed populates the database with sample data
func main() {
	var cfg config.Config
	flag.StringVar(&cfg.CoreDBConnectionString, "db", "", "coreDB connection string (eg. postgres://postgres:1234@localhost:5432/b2b_1136)")
	flag.Parse()

	if cfg.CoreDBConnectionString == "" {
		log.Fatal("Database connection string is required")
	}

	// Initialize database
	db, err := database.InitDB(cfg.CoreDBConnectionString)
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	// Run migrations
	err = database.AutoMigrate(db)
	if err != nil {
		log.Fatalf("Failed to run migrations: %v", err)
	}

	// Create sample users
	err = createSampleUsers(db)
	if err != nil {
		log.Fatalf("Failed to create sample users: %v", err)
	}

	fmt.Println("Database initialized successfully with sample data")
}

func createSampleUsers(db *gorm.DB) error {
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

	return nil
}

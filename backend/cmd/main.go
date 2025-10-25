package main

import (
	"flag"
	"fmt"
	"log"

	"com.github.hackathon-kifiya.fraud-detection-system/cmd/router"
	"com.github.hackathon-kifiya.fraud-detection-system/config"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/database"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/repository"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/api/handler"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"gorm.io/gorm"
)

func main() {
	var cfg config.Config
	var seedDB bool
	flag.IntVar(&cfg.Port, "port", 4000, "api server port")
	flag.StringVar(&cfg.Env, "env", "development", "Environment (development|staging|production)")
	flag.StringVar(&cfg.BaseUrl, "baseUrl", "", "Base url")
	flag.StringVar(&cfg.CoreDBConnectionString, "db", "", "coreDB connection string (eg. postgres://postgres:1234@localhost:5432/b2b_1136)")
	flag.StringVar(&cfg.FrontendUrl, "frontend_base_url", "", "frontend base url")
	flag.StringVar(&cfg.MigrationFileLocation, "migration_file_dir", "", "migration file dir")
	flag.BoolVar(&seedDB, "seed", false, "seed database with sample data and exit")
	flag.Parse()

	// Initialize database
	var db *gorm.DB
	var err error

	if cfg.CoreDBConnectionString == "" {
		log.Println("No database connection string provided, using in-memory SQLite for testing")
		db, err = database.InitSQLite(":memory:")
	} else {
		db, err = database.InitDB(cfg.CoreDBConnectionString)
	}

	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	// Run migrations
	err = database.AutoMigrate(db)
	if err != nil {
		log.Fatalf("Failed to run migrations: %v", err)
	}

	// If seed flag is set, seed database and exit
	if seedDB {
		err = seedDatabase(db)
		if err != nil {
			log.Fatalf("Failed to seed database: %v", err)
		}
		log.Println("Database seeded successfully")
		return
	}

	// Initialize repositories
	userRepo := repository.NewUserRepository(db)
	flaggedItemRepo := repository.NewFlaggedItemRepository(db)
	auditNoteRepo := repository.NewAuditNoteRepository(db)
	auditLogRepo := repository.NewAuditLogRepository(db)

	// Initialize services
	jwtSecret := "your-secret-key" // In production, use environment variable
	userService := service.NewUserService(userRepo, jwtSecret)
	flaggedItemService := service.NewFlaggedItemService(flaggedItemRepo)
	auditService := service.NewAuditService(flaggedItemRepo, auditNoteRepo, auditLogRepo)

	// Initialize router
	r := router.Init()

	// Register health endpoint
	router.RegisterHealthEndpoint()

	// Initialize handlers
	handler.InitUserHandler(userService, r)
	handler.InitFlaggedItemHandler(flaggedItemService, r)
	handler.InitAuditHandler(auditService, r)

	addr := fmt.Sprintf(":%d", cfg.Port)

	log.Printf("Server starting on port %d", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

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

	return nil
}

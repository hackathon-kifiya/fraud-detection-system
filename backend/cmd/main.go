package main

import (
	"flag"
	"fmt"
	"log"

	"com.github.hackathon-kifiya.fraud-detection-system/cmd/router"
	"com.github.hackathon-kifiya.fraud-detection-system/config"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/client"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/database"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/adapter/repository"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/api/handler"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"gorm.io/gorm"
)

func main() {
	var cfg config.Config
	var seedDB bool
	flag.IntVar(&cfg.Port, "port", 8080, "api server port")
	flag.StringVar(&cfg.Env, "env", "development", "Environment (development|staging|production)")
	flag.StringVar(&cfg.BaseUrl, "baseUrl", "", "Base url")
	flag.StringVar(&cfg.CoreDBConnectionString, "db", "", "coreDB connection string (eg. postgres://postgres:1234@localhost:5432/b2b_1136)")
	flag.StringVar(&cfg.FrontendUrl, "frontend_base_url", "", "frontend base url")
	flag.StringVar(&cfg.MigrationFileLocation, "migration_file_dir", "", "migration file dir")
	flag.StringVar(&cfg.RuleEngineURL, "rule_engine_url", "", "rule engine URL")
	flag.StringVar(&cfg.AnomalyDetectionEngineURL, "anomaly_detection_engine_url", "", "anomaly detection engine URL")
	flag.StringVar(&cfg.PredictiveEngineURL, "predictive_engine_url", "", "predictive engine URL")
	flag.StringVar(&cfg.RiskAggregationEngineURL, "risk_aggregation_engine_url", "", "risk aggregation engine URL")
	flag.StringVar(&cfg.PythonStatsURL, "python_stats_url", "", "python stats URL")
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
	systemConfigRepo := repository.NewSystemConfigRepository(db)
	caseAssignmentRepo := repository.NewCaseAssignmentRepository(db)
	performanceReportRepo := repository.NewPerformanceReportRepository(db)
	kpiMetricsRepo := repository.NewKPIMetricsRepository(db)
	callbackRepo := repository.NewCallbackRepository(db)

	// Initialize engine clients

	// ruleEngineClient := client.NewRuleEngineClient(cfg.RuleEngineURL)
	anomalyDetectionClient := client.NewAnomalyDetectionEngineClient(cfg.AnomalyDetectionEngineURL)
	predictiveEngineClient := client.NewPredictiveEngineClient(cfg.PredictiveEngineURL)
	riskAggregationClient := client.NewRiskAggregationEngineClient(cfg.RiskAggregationEngineURL)

	// Initialize clients (for future use)
	_ = anomalyDetectionClient
	_ = predictiveEngineClient
	_ = riskAggregationClient

	// Initialize services

	//TODO: use environment variable

	jwtSecret := "your-secret-key"
	userService := service.NewUserService(userRepo, jwtSecret)
	flaggedItemService := service.NewFlaggedItemService(flaggedItemRepo)
	// ruleEvaluationService := service.NewRuleEvaluationService(ruleEngineClient, flaggedItemRepo, flaggedItemService)
	auditService := service.NewAuditService(flaggedItemRepo, auditNoteRepo, auditLogRepo, caseAssignmentRepo)
	adminService := service.NewAdminService(flaggedItemRepo, auditLogRepo, systemConfigRepo, caseAssignmentRepo, performanceReportRepo, kpiMetricsRepo, userRepo)
	callbackService := service.NewCallbackService(callbackRepo)

	// Initialize router
	r := router.Init()

	// Register health endpoint
	router.RegisterHealthEndpoint()

	// Initialize handlers
	handler.InitUserHandler(userService, r)
	handler.InitFlaggedItemHandler(flaggedItemService, r)
	handler.InitAuditHandler(auditService, r)
	handler.InitAdminHandler(adminService, r)
	handler.InitCallbackHandler(callbackService, r)

	addr := fmt.Sprintf(":%d", cfg.Port)

	log.Printf("Server starting on port %d", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

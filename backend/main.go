package main

import (
	"log"
	"os"

	"fraud-detection-backend/db"
	"fraud-detection-backend/handlers"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize database
	database, err := db.NewDB()
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer database.Close()

	// Get engine URL from environment
	engineURL := os.Getenv("ENGINE_URL")
	if engineURL == "" {
		engineURL = "http://engine:5001"
	}

	// Initialize handlers
	uploadHandler := handlers.NewUploadHandler(database)
	detectionHandler := handlers.NewDetectionHandler(database, engineURL)
	flaggedHandler := handlers.NewFlaggedHandler(database)

	// Set Gin mode
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create Gin router
	router := gin.Default()

	// Configure CORS
	config := cors.DefaultConfig()
	config.AllowOrigins = []string{"http://localhost:3001", "http://frontend:3000"}
	config.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{"Origin", "Content-Type", "Accept", "Authorization"}
	config.AllowCredentials = true
	router.Use(cors.New(config))

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "healthy",
			"service": "fraud-detection-backend",
			"version": "1.0.0",
		})
	})

	// API routes
	api := router.Group("/api")
	{
		// Detection endpoints
		api.POST("/detect", detectionHandler.TriggerDetection)
		api.POST("/detect/:type", detectionHandler.TriggerDetectionByType)
		api.GET("/detect/status", detectionHandler.GetDetectionStatus)

		// Flagged items endpoints
		api.GET("/flagged", flaggedHandler.GetFlaggedItems)
		api.GET("/flagged/:id", flaggedHandler.GetFlaggedItem)
		api.POST("/verify/:id", flaggedHandler.VerifyFlaggedItem)
		api.GET("/flagged/stats", flaggedHandler.GetFlaggedStats)
	}

	// Upload endpoints
	router.POST("/upload/transactions", uploadHandler.UploadTransactions)
	router.POST("/upload/loan_requests", uploadHandler.UploadLoanRequests)
	router.POST("/upload/credit_history", uploadHandler.UploadCreditHistory)
	router.POST("/upload/kyc", uploadHandler.UploadKYC)
	router.POST("/upload/repayments", uploadHandler.UploadRepayments)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Starting Fraud Detection Backend on port %s", port)
	log.Printf("Engine URL: %s", engineURL)

	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

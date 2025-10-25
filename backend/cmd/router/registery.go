package router

import (
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

var engine *gin.Engine

func Init() *gin.Engine {
	engine = gin.Default()

	// Configure CORS
	config := cors.Config{
		AllowOrigins:     []string{"http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization", "X-Requested-With"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}

	engine.Use(cors.New(config))

	return engine
}

func Get() *gin.Engine {
	return engine
}

func RegisterHealthEndpoint() {
	if engine != nil {
		engine.GET("/health", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"status":       "ok",
				"service-name": "fraud-detection-backend",
				"version":      "v0.1.0"})
		})
	}
}

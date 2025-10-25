// api/health.go
package handler

import (
	"com.github.hackathon-kifiya.fraud-detection-system/cmd/router"
	"github.com/gin-gonic/gin"
)

func init() {
	// Register health endpoint when router is available
	router.RegisterHealthEndpoint()
}

func HealthHandler(c *gin.Context) {
	c.JSON(200, gin.H{
		"status":       "ok",
		"service-name": "fraud-detection-backend",
		"version":      "v0.1.0"})
}

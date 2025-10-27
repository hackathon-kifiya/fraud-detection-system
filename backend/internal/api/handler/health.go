// api/health.go
package handler

import (
	"com.github.hackathon-kifiya.fraud-detection-system/cmd/router"
	"github.com/gin-gonic/gin"
)

func init() {
	router.RegisterHealthEndpoint()
}

func HealthHandler(c *gin.Context) {
	c.JSON(200, gin.H{
		"status":       "healthy",
		"service-name": "fraud-detection-backend",
		"version":      "v0.1.0"})
}

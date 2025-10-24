// api/health.go
package handler

import (
	"com.github.hackathon-kifiya.fraud-detection-system/cmd/router"
	"github.com/gin-gonic/gin"
)

func init() {
	r := router.Get()
	r.GET("/health", healthHandler)
}

func healthHandler(c *gin.Context) {
	c.JSON(200, gin.H{
		"status":       "ok",
		"service-name": "",
		"version":      "0.1.0"})
}

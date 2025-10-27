package router

import (
	"strings"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

var engine *gin.Engine

type RouterConfig struct {
	AllowedOrigins string
}

func Init(cfg *RouterConfig) *gin.Engine {
	engine = gin.Default()

	// Parse allowed origins from config
	var allowOrigins []string
	if cfg != nil && cfg.AllowedOrigins != "" {
		// Split by comma and clean up whitespace
		origins := strings.Split(cfg.AllowedOrigins, ",")
		for _, origin := range origins {
			allowOrigins = append(allowOrigins, strings.TrimSpace(origin))
		}
	}

	// Default origins if none provided
	if len(allowOrigins) == 0 {
		allowOrigins = []string{"http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"}
	}

	// Configure CORS
	config := cors.Config{
		AllowOrigins:     allowOrigins,
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

func RegisterSwaggerEndpoint(r *gin.Engine) {
	if r == nil {
		return
	}

	// Swagger JSON endpoint
	r.GET("/swagger/doc.json", func(c *gin.Context) {
		c.JSON(200, getSwaggerJSON())
	})

	// Swagger UI endpoint
	r.GET("/swagger", func(c *gin.Context) {
		c.Data(200, "text/html", []byte(getSwaggerUI()))
	})
}

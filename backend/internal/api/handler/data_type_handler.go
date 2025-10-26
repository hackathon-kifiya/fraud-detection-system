package handler

import (
	"net/http"
	"strconv"

	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/domain"
	"com.github.hackathon-kifiya.fraud-detection-system/internal/core/service"
	"github.com/gin-gonic/gin"
)

var dataTypeService *service.DataTypeService

// InitDataTypeHandler initializes the data type handler with dependencies
func InitDataTypeHandler(svc *service.DataTypeService, r *gin.Engine) {
	dataTypeService = svc

	// Public routes (for internal services to fetch data types)
	r.GET("/api/data-types/active", getActiveDataTypesHandler)

	// Protected routes
	protected := r.Group("/api/data-types")
	protected.Use(authMiddleware())
	{
		protected.POST("", createDataTypeHandler)
		protected.GET("", listDataTypesHandler)
		protected.GET("/search", searchDataTypesHandler)
		protected.GET("/:id", getDataTypeHandler)
		protected.GET("/name/:name", getDataTypeByNameHandler)
		protected.PUT("/:id", updateDataTypeHandler)
	}
}

// createDataTypeHandler handles creating a new data type
func createDataTypeHandler(c *gin.Context) {
	var req domain.CreateDataTypeRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get current user from context
	userID, exists := c.Get("user_id")
	if exists && userID != nil {
		req.CreatedBy = userID.(string)
	}

	dataType, err := dataTypeService.CreateDataType(c.Request.Context(), req)
	if err != nil {
		if err == service.ErrDuplicateDataType {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}
		if err == service.ErrInvalidSchema {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, dataType)
}

// getDataTypeHandler handles getting a data type by ID
func getDataTypeHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	dataType, err := dataTypeService.GetDataType(c.Request.Context(), id)
	if err != nil {
		if err == service.ErrDataTypeNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, dataType)
}

// getDataTypeByNameHandler handles getting a data type by name
func getDataTypeByNameHandler(c *gin.Context) {
	name := c.Param("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "name is required"})
		return
	}

	dataType, err := dataTypeService.GetDataTypeByName(c.Request.Context(), name)
	if err != nil {
		if err == service.ErrDataTypeNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, dataType)
}

// listDataTypesHandler handles listing data types
func listDataTypesHandler(c *gin.Context) {
	limitStr := c.DefaultQuery("limit", "10")
	offsetStr := c.DefaultQuery("offset", "0")

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit <= 0 {
		limit = 10
	}

	offset, err := strconv.Atoi(offsetStr)
	if err != nil || offset < 0 {
		offset = 0
	}

	response, err := dataTypeService.ListDataTypes(c.Request.Context(), limit, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// updateDataTypeHandler handles updating a data type
func updateDataTypeHandler(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	var req domain.UpdateDataTypeRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get current user from context
	userID, exists := c.Get("user_id")
	if exists && userID != nil {
		updatedBy := userID.(string)
		req.UpdatedBy = &updatedBy
	}

	dataType, err := dataTypeService.UpdateDataType(c.Request.Context(), id, req)
	if err != nil {
		if err == service.ErrDataTypeNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
			return
		}
		if err == service.ErrDuplicateDataType {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}
		if err == service.ErrInvalidSchema {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, dataType)
}

// getActiveDataTypesHandler handles getting active data types (public endpoint)
func getActiveDataTypesHandler(c *gin.Context) {
	dataTypes, err := dataTypeService.GetActiveDataTypes(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data_types": dataTypes})
}

// searchDataTypesHandler handles searching data types
func searchDataTypesHandler(c *gin.Context) {
	query := c.Query("q")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "query parameter 'q' is required"})
		return
	}

	dataTypes, err := dataTypeService.SearchDataTypes(c.Request.Context(), query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data_types": dataTypes})
}

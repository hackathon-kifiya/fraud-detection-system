package router

// getSwaggerJSON returns the Swagger/OpenAPI JSON
func getSwaggerJSON() map[string]interface{} {
	return map[string]interface{}{
		"openapi": "3.0.0",
		"info": map[string]interface{}{
			"title":       "Fraud Detection System API",
			"description": "API for managing fraud detection, flagged items, users, and data types",
			"version":     "1.0.0",
			"contact": map[string]interface{}{
				"name":  "API Support",
				"email": "support@example.com",
			},
		},
		"servers": []map[string]interface{}{
			{
				"url":         "http://localhost:8080",
				"description": "Development server",
			},
		},
		"tags": []map[string]interface{}{
			{
				"name":        "Health",
				"description": "Health check endpoints",
			},
			{
				"name":        "Authentication",
				"description": "User authentication and registration",
			},
			{
				"name":        "Users",
				"description": "User management",
			},
			{
				"name":        "Flagged Items",
				"description": "Flagged items for fraud detection",
			},
			{
				"name":        "Data Types",
				"description": "Data type management for flexible schema definitions",
			},
			{
				"name":        "Decision",
				"description": "Decision service integration",
			},
			{
				"name":        "Audit",
				"description": "Audit logs and notes",
			},
			{
				"name":        "Admin",
				"description": "Administrative functions",
			},
			{
				"name":        "Callbacks",
				"description": "Webhook callbacks configuration",
			},
		},
		"paths": map[string]interface{}{
			"/health": map[string]interface{}{
				"get": map[string]interface{}{
					"tags": []string{"Health"},
					"summary": "Health check",
					"description": "Check if the API is running",
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "Service is healthy",
							"content": map[string]interface{}{
								"application/json": map[string]interface{}{
									"schema": map[string]interface{}{
										"type": "object",
										"properties": map[string]interface{}{
											"status": map[string]interface{}{
												"type":    "string",
												"example": "ok",
											},
											"service-name": map[string]interface{}{
												"type":    "string",
												"example": "fraud-detection-backend",
											},
											"version": map[string]interface{}{
												"type":    "string",
												"example": "v0.1.0",
											},
										},
									},
								},
							},
						},
					},
				},
			},
			"/api/auth/register": map[string]interface{}{
				"post": map[string]interface{}{
					"tags":        []string{"Authentication"},
					"summary":     "Register a new user",
					"description": "Create a new user account",
					"requestBody": map[string]interface{}{
						"required": true,
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"schema": map[string]interface{}{
									"$ref": "#/components/schemas/CreateUserRequest",
								},
							},
						},
					},
					"responses": map[string]interface{}{
						"201": map[string]interface{}{
							"description": "User created successfully",
						},
						"400": map[string]interface{}{
							"description": "Invalid request",
						},
						"409": map[string]interface{}{
							"description": "User already exists",
						},
					},
				},
			},
			"/api/auth/login": map[string]interface{}{
				"post": map[string]interface{}{
					"tags":        []string{"Authentication"},
					"summary":     "User login",
					"description": "Authenticate user and get JWT token",
					"requestBody": map[string]interface{}{
						"required": true,
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"schema": map[string]interface{}{
									"type": "object",
									"required": []string{"email", "password"},
									"properties": map[string]interface{}{
										"email": map[string]interface{}{
											"type":    "string",
											"format":  "email",
											"example": "user@example.com",
										},
										"password": map[string]interface{}{
											"type":    "string",
											"format":  "password",
											"example": "password123",
										},
									},
								},
							},
						},
					},
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "Login successful",
						},
						"401": map[string]interface{}{
							"description": "Invalid credentials",
						},
					},
				},
			},
			"/api/data-types": map[string]interface{}{
				"get": map[string]interface{}{
					"tags":        []string{"Data Types"},
					"summary":     "List data types",
					"description": "Get paginated list of data types",
					"security": []map[string]interface{}{
						{
							"bearerAuth": []string{},
						},
					},
					"parameters": []map[string]interface{}{
						{
							"name":        "limit",
							"in":          "query",
							"schema":      map[string]interface{}{"type": "integer", "default": 10},
							"description": "Number of results",
						},
						{
							"name":        "offset",
							"in":          "query",
							"schema":      map[string]interface{}{"type": "integer", "default": 0},
							"description": "Pagination offset",
						},
					},
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "List of data types",
						},
					},
				},
				"post": map[string]interface{}{
					"tags":        []string{"Data Types"},
					"summary":     "Create data type",
					"description": "Create a new data type with schema definition",
					"security": []map[string]interface{}{
						{
							"bearerAuth": []string{},
						},
					},
					"requestBody": map[string]interface{}{
						"required": true,
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"schema": map[string]interface{}{
									"$ref": "#/components/schemas/CreateDataTypeRequest",
								},
							},
						},
					},
					"responses": map[string]interface{}{
						"201": map[string]interface{}{
							"description": "Data type created successfully",
						},
						"400": map[string]interface{}{
							"description": "Invalid request",
						},
						"409": map[string]interface{}{
							"description": "Data type already exists",
						},
					},
				},
			},
			"/api/data-types/{id}": map[string]interface{}{
				"get": map[string]interface{}{
					"tags":        []string{"Data Types"},
					"summary":     "Get data type by ID",
					"description": "Retrieve a specific data type",
					"security": []map[string]interface{}{
						{
							"bearerAuth": []string{},
						},
					},
					"parameters": []map[string]interface{}{
						{
							"name":        "id",
							"in":          "path",
							"required":    true,
							"schema":      map[string]interface{}{"type": "string"},
							"description": "Data type ID",
						},
					},
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "Data type found",
						},
						"404": map[string]interface{}{
							"description": "Data type not found",
						},
					},
				},
				"put": map[string]interface{}{
					"tags":        []string{"Data Types"},
					"summary":     "Update data type",
					"description": "Update an existing data type",
					"security": []map[string]interface{}{
						{
							"bearerAuth": []string{},
						},
					},
					"parameters": []map[string]interface{}{
						{
							"name":        "id",
							"in":          "path",
							"required":    true,
							"schema":      map[string]interface{}{"type": "string"},
							"description": "Data type ID",
						},
					},
					"requestBody": map[string]interface{}{
						"required": true,
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"schema": map[string]interface{}{
									"$ref": "#/components/schemas/UpdateDataTypeRequest",
								},
							},
						},
					},
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "Data type updated successfully",
						},
						"404": map[string]interface{}{
							"description": "Data type not found",
						},
					},
				},
				"delete": map[string]interface{}{
					"tags":        []string{"Data Types"},
					"summary":     "Delete data type",
					"description": "Delete a data type",
					"security": []map[string]interface{}{
						{
							"bearerAuth": []string{},
						},
					},
					"parameters": []map[string]interface{}{
						{
							"name":        "id",
							"in":          "path",
							"required":    true,
							"schema":      map[string]interface{}{"type": "string"},
							"description": "Data type ID",
						},
					},
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "Data type deleted successfully",
						},
						"404": map[string]interface{}{
							"description": "Data type not found",
						},
					},
				},
			},
			"/api/data-types/active": map[string]interface{}{
				"get": map[string]interface{}{
					"tags":        []string{"Data Types"},
					"summary":     "Get active data types",
					"description": "Get all active data types (public endpoint)",
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "List of active data types",
						},
					},
				},
			},
			"/api/data-types/search": map[string]interface{}{
				"get": map[string]interface{}{
					"tags":        []string{"Data Types"},
					"summary":     "Search data types",
					"description": "Search data types by query string",
					"security": []map[string]interface{}{
						{
							"bearerAuth": []string{},
						},
					},
					"parameters": []map[string]interface{}{
						{
							"name":        "q",
							"in":          "query",
							"required":    true,
							"schema":      map[string]interface{}{"type": "string"},
							"description": "Search query",
						},
					},
					"responses": map[string]interface{}{
						"200": map[string]interface{}{
							"description": "Search results",
						},
					},
				},
			},
		},
		"components": map[string]interface{}{
			"securitySchemes": map[string]interface{}{
				"bearerAuth": map[string]interface{}{
					"type":         "http",
					"scheme":       "bearer",
					"bearerFormat": "JWT",
					"description":  "JWT token authentication",
				},
			},
			"schemas": map[string]interface{}{
				"CreateUserRequest": map[string]interface{}{
					"type": "object",
					"required": []string{"email", "password", "first_name", "last_name", "role"},
					"properties": map[string]interface{}{
						"email": map[string]interface{}{
							"type":   "string",
							"format": "email",
						},
						"password": map[string]interface{}{
							"type": "string",
						},
						"first_name": map[string]interface{}{
							"type": "string",
						},
						"last_name": map[string]interface{}{
							"type": "string",
						},
						"role": map[string]interface{}{
							"type":    "string",
							"enum":    []string{"admin", "analyst", "viewer"},
						},
					},
				},
				"CreateDataTypeRequest": map[string]interface{}{
					"type": "object",
					"required": []string{"data_type", "name", "schema_definition"},
					"properties": map[string]interface{}{
						"data_type": map[string]interface{}{
							"type": "string",
						},
						"name": map[string]interface{}{
							"type": "string",
						},
						"description": map[string]interface{}{
							"type": "string",
						},
						"schema_definition": map[string]interface{}{
							"type":    "object",
							"example": map[string]interface{}{
								"fields": map[string]string{
									"amount":  "Double",
									"merchant": "String",
								},
								"required": []string{"amount"},
							},
						},
						"sample_data": map[string]interface{}{
							"type": "object",
						},
						"status": map[string]interface{}{
							"type":    "string",
							"enum":    []string{"ACTIVE", "INACTIVE", "DRAFT"},
							"default": "ACTIVE",
						},
					},
				},
				"UpdateDataTypeRequest": map[string]interface{}{
					"type": "object",
					"properties": map[string]interface{}{
						"data_type": map[string]interface{}{
							"type": "string",
						},
						"name": map[string]interface{}{
							"type": "string",
						},
						"description": map[string]interface{}{
							"type": "string",
						},
						"schema_definition": map[string]interface{}{
							"type": "object",
						},
						"sample_data": map[string]interface{}{
							"type": "object",
						},
						"status": map[string]interface{}{
							"type":    "string",
							"enum":    []string{"ACTIVE", "INACTIVE", "DRAFT"},
						},
					},
				},
			},
		},
	}
}

// getSwaggerUI returns the Swagger UI HTML
func getSwaggerUI() string {
	return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fraud Detection System API - Swagger UI</title>
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: '/swagger/doc.json',
      dom_id: '#swagger-ui',
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.presets.standalone
      ],
      layout: "BaseLayout",
      deepLinking: true,
      showExtensions: true,
      showCommonExtensions: true
    })
  </script>
</body>
</html>`
}


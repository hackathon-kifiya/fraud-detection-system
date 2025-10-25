# User Management Module

This module provides comprehensive user management functionality for the fraud detection system, including authentication, authorization, and user CRUD operations.

## Features

- **User Registration & Authentication**: Secure user registration and login with JWT tokens
- **Role-Based Access Control**: Three user roles (admin, analyst, viewer)
- **Password Management**: Secure password hashing and change functionality
- **User CRUD Operations**: Create, read, update, and delete users
- **Database Integration**: Uses GORM ORM with PostgreSQL

## API Endpoints

### Public Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token

### Protected Endpoints (Require JWT token)

- `GET /api/users` - List all users (with pagination)
- `GET /api/users/:id` - Get user by ID
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user
- `POST /api/users/:id/change-password` - Change user password

## User Roles

- **admin**: Full access to all operations
- **analyst**: Can view and analyze data
- **viewer**: Read-only access

## Database Schema

The users table includes:
- `id`: UUID primary key
- `email`: Unique email address
- `password_hash`: Hashed password (never exposed in API)
- `first_name`: User's first name
- `last_name`: User's last name
- `role`: User role (admin/analyst/viewer)
- `is_active`: Account status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Usage

### Starting the Server

```bash
go run cmd/main.go -db="postgres://user:password@localhost:5432/dbname"
```

2. **Seed database with sample data:**
```bash
go run cmd/main.go -db="postgres://user:password@localhost:5432/dbname" -seed
```

### Example API Calls

#### Register a new user
```bash
curl -X POST http://localhost:4000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "role": "analyst"
  }'
```

#### Login
```bash
curl -X POST http://localhost:4000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

#### Access protected endpoint
```bash
curl -X GET http://localhost:4000/api/users \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Features

- Password hashing using bcrypt
- JWT token authentication
- Role-based authorization
- Input validation
- SQL injection protection (via GORM)

## Dependencies

- GORM for database operations
- JWT for authentication
- bcrypt for password hashing
- Gin for HTTP routing
- PostgreSQL driver

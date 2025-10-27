# Fraud Detection Backend Makefile

.PHONY: build run init-db clean test

# Build the main application
build:
	go build -o bin/main cmd/main.go

# Run the main application
run:
	go run cmd/main.go -db="$(DB_URL)"

# Seed database with sample data
seed-db:
	go run cmd/main.go -db="$(DB_URL)" -seed

# Run both seeding and server
start: seed-db run

# Clean build artifacts
clean:
	rm -rf bin/

# Run tests
test:
	go test ./...

# Install dependencies
deps:
	go mod tidy

# Example usage:
# make run DB_URL="postgres://user:pass@localhost:5432/dbname"
# make seed-db DB_URL="postgres://user:pass@localhost:5432/dbname"
# make start DB_URL="postgres://user:pass@localhost:5432/dbname"

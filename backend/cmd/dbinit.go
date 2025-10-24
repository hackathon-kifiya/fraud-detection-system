package main

import (
	"context"
	"database/sql"
	"errors"
	"log"
	"os"

	"com.github.hackathon-kifiya.fraud-detection-system/config"
	_ "github.com/jackc/pgx/v4/stdlib"
)

var (
	ErrFailedToExecuteMigration  = errors.New(" failed to execute migration")
	ErrFailedToReadMigrationFile = errors.New(" failed to read migration file")
	ErrFailedToOpenDB            = errors.New(" failed to open database connection")
	ErrFailedToConnectDB         = errors.New(" failed to connect with db")
)

func InitDB(cfg *config.Config) *sql.DB {
	db, err := sql.Open("pgx", cfg.CoreDBConnectionString)
	if err != nil {
		log.Panic(err.Error())
	}
	ctx := context.Background()
	if err := db.PingContext(ctx); err != nil {
		log.Panic(err.Error())
	}

	switch cfg.Env {
	case "development":
		InitDBDevelopment(db, cfg.MigrationFileLocation, cfg)
	case "staging":
		InitDBStaging(db, cfg.MigrationFileLocation, cfg)
	case "production":
		InitDBProduction(db, cfg.MigrationFileLocation, cfg)
	}

	return db
}

func InitDBDevelopment(db *sql.DB, file_location string, cfg *config.Config) {
	// Create a migrations table if it doesn't exist
	_, err := db.Exec(`
	CREATE TABLE IF NOT EXISTS migrations (
		id SERIAL PRIMARY KEY,
		name TEXT NOT NULL UNIQUE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`)
	if err != nil {
		log.Fatalf("Error creating migrations table: %v", err)
	}

	// ddl
	err = runMigration(db, file_location+`/core_db.sql`)
	if err != nil {
		log.Fatalf("Error running ddl migration: %v", err)
	}

	// functions
	err = runMigration(db, file_location+"/core_db_functions.sql")
	if err != nil {
		log.Fatalf("Error running function migration: %v", err)
	}

	// Check if the seed migration has already been applied
	if !migrationExists(db, "core_init_migration_script.sql") {
		// seed
		err = runMigration(db, file_location+"/core_init_migration_script.sql")
		if err != nil {
			log.Fatalf("Error running seed migration: %v", err)
		}

		// Record the migration
		_, err = db.Exec("INSERT INTO migrations (name) VALUES ($1)", "core_init_migration_script.sql")
		if err != nil {
			log.Fatalf("Error recording seed migration: %v", err)
		}
	}
}

func migrationExists(db *sql.DB, migrationName string) bool {
	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM migrations WHERE name=$1)", migrationName).Scan(&exists)
	if err != nil {
		log.Fatalf("Error checking migration existence: %v", err)
	}
	return exists
}

func InitDBStaging(db *sql.DB, file_location string, cfg *config.Config) {
}

func InitDBProduction(db *sql.DB, file_location string, cfg *config.Config) {
}

func runMigration(db *sql.DB, filename string) error {
	// Read
	sqlBytes, err := os.ReadFile(filename)
	if err != nil {
		log.Panic(ErrFailedToReadMigrationFile)
	}

	// Execute
	_, err = db.Exec(string(sqlBytes))
	if err != nil {
		log.Panic(err.Error(), filename)
	}
	return nil
}

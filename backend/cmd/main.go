package main

import (
	"flag"
	"fmt"

	"com.github.hackathon-kifiya.fraud-detection-system/cmd/router"
	"com.github.hackathon-kifiya.fraud-detection-system/config"
)

func main() {

	var cfg config.Config
	flag.IntVar(&cfg.Port, "port", 4000, "api server port")
	flag.StringVar(&cfg.Env, "env", "development", "Environment (development|staging|production)")
	flag.StringVar(&cfg.BaseUrl, "baseUrl", "", "Base url")
	flag.StringVar(&cfg.CoreDBConnectionString, "db", "", "coreDB connection string (eg. postgres://postgres:1234@localhost:5432/b2b_1136)")
	flag.StringVar(&cfg.FrontendUrl, "frontend_base_url", "", "frontend base url")
	flag.StringVar(&cfg.MigrationFileLocation, "migration_file_dir", "", "migration file dir")

	// db_pool := InitDB(&cfg)

	r := router.Init()
	addr := fmt.Sprintf(":%d", cfg.Port)
	r.Run(addr)
}

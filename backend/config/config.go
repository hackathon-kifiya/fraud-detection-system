package config

type Config struct {
	Port                      int
	Env                       string
	BaseUrl                   string
	FrontendUrl               string
	CoreDBConnectionString    string
	MigrationFileLocation     string
	RuleEngineURL             string
	AnomalyDetectionEngineURL string
	PredictiveEngineURL       string
	DecisionServiceURL        string
	DataManagementServiceURL  string
	PythonStatsURL            string
	EnableSwagger             bool
	CorsAllowedOrigins        string
}

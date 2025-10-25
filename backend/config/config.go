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
	RiskAggregationEngineURL  string
	PythonStatsURL            string
}

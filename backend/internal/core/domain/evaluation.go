package domain

// EvaluationRequest represents a request to evaluate data
type EvaluationRequest struct {
	DataType string                   `json:"dataType" binding:"required"`
	Facts    []map[string]interface{} `json:"facts" binding:"required"`
}

// EvaluationResult represents the complete evaluation result
type EvaluationResult struct {
	EntityID              string            `json:"entity_id"`
	DataType              string            `json:"data_type"`
	RuleEngineScore       float64           `json:"rule_engine_score"`
	AnomalyDetectionScore float64           `json:"anomaly_detection_score"`
	PredictiveEngineScore float64           `json:"predictive_engine_score"`
	FinalScore            float64           `json:"final_score"`
	Decision              string            `json:"decision"` // "auto_approve", "auto_reject", "human_review"
	Breakdown             interface{}       `json:"breakdown,omitempty"`
	ActionTaken           string            `json:"action_taken"` // "callback_invoked", "case_created"
	FlaggedItemID         *string           `json:"flagged_item_id,omitempty"`
	Errors                map[string]string `json:"errors,omitempty"`
}

// EvaluationResponse represents the API response
type EvaluationResponse struct {
	Success bool              `json:"success"`
	Result  *EvaluationResult `json:"result"`
	Message string            `json:"message,omitempty"`
}

"""Use case for making decisions."""

from domain.models import (
    DecisionRequest, 
    DecisionResult, 
    DecisionConfigModel,
    DecisionType
)
from domain.repository import DecisionConfigRepository


class DecisionService:
    """Service for making fraud detection decisions."""
    
    def __init__(self, config_repository: DecisionConfigRepository):
        self.config_repository = config_repository
    
    def make_decision(self, request: DecisionRequest) -> DecisionResult:
        """Make a decision based on aggregated engine scores."""
        # Get current configuration
        config = self.config_repository.get_config()
        
        # Calculate final weighted score
        final_score = self._calculate_final_score(
            config,
            request.rule_engine_score,
            request.anomaly_detection_score,
            request.predictive_engine_score
        )
        
        # Convert to percentage
        final_score_percent = final_score * 100
        
        # Determine decision
        decision = self._get_decision(final_score_percent, config)
        
        # Calculate confidence
        confidence = self._calculate_confidence(decision, final_score_percent, config)
        
        # Create breakdown
        breakdown = self._create_breakdown(
            config,
            request.rule_engine_score,
            request.anomaly_detection_score,
            request.predictive_engine_score
        )
        
        return DecisionResult(
            entity_id=request.entity_id,
            final_score=final_score,
            final_score_percent=final_score_percent,
            decision=decision,
            breakdown=breakdown,
            confidence=confidence
        )
    
    def _calculate_final_score(
        self, 
        config: DecisionConfigModel,
        rule_score: float, 
        anomaly_score: float, 
        predictive_score: float
    ) -> float:
        """Calculate final weighted score."""
        if config.model_based_scoring:
            # Future: Use ML model to determine weights
            # For now, fall back to manual weights
            pass
        
        # Calculate weighted average
        weighted_sum = (
            rule_score * config.rule_engine_weight +
            anomaly_score * config.anomaly_detection_weight +
            predictive_score * config.predictive_engine_weight
        )
        final_score = weighted_sum / 100.0
        
        return final_score
    
    def _get_decision(
        self, 
        score_percent: float, 
        config: DecisionConfigModel
    ) -> str:
        """Determine decision based on thresholds."""
        if score_percent <= config.auto_approve_threshold:
            decision = DecisionType.AUTO_APPROVE
        elif score_percent >= config.auto_reject_threshold:
            decision = DecisionType.AUTO_REJECT
        else:
            decision = DecisionType.HUMAN_REVIEW
        
        return decision
    
    def _calculate_confidence(
        self, 
        decision: str, 
        score_percent: float, 
        config: DecisionConfigModel
    ) -> float:
        """Calculate decision confidence."""
        if decision == DecisionType.AUTO_APPROVE:
            confidence = 1.0 - (score_percent / config.auto_approve_threshold)
        elif decision == DecisionType.AUTO_REJECT:
            confidence = 1.0 - ((100 - score_percent) / (100 - config.auto_reject_threshold))
        else:
            confidence = 0.5
        
        return max(0.0, min(1.0, confidence))
    
    def _create_breakdown(
        self,
        config: DecisionConfigModel,
        rule_score: float,
        anomaly_score: float,
        predictive_score: float
    ) -> dict:
        """Create score breakdown by engine."""
        return {
            "rule_engine": {
                "score": rule_score,
                "weight": config.rule_engine_weight,
                "contribution": rule_score * config.rule_engine_weight
            },
            "anomaly_detection": {
                "score": anomaly_score,
                "weight": config.anomaly_detection_weight,
                "contribution": anomaly_score * config.anomaly_detection_weight
            },
            "predictive_engine": {
                "score": predictive_score,
                "weight": config.predictive_engine_weight,
                "contribution": predictive_score * config.predictive_engine_weight
            }
        }


class ConfigService:
    """Service for managing configuration."""
    
    def __init__(self, config_repository: DecisionConfigRepository):
        self.config_repository = config_repository
    
    def get_config(self) -> DecisionConfigModel:
        """Get current configuration."""
        return self.config_repository.get_config()
    
    def update_config(self, config: DecisionConfigModel) -> dict:
        """Update configuration."""
        return self.config_repository.update_config(config)


"""
SHAP Explainer Service
Provides interpretable explanations for model predictions
"""
from typing import Any, Dict, List

import numpy as np
import shap

from app.core.logging import get_logger

logger = get_logger(__name__)


class ShapExplainerService:
    """Service for generating SHAP explanations"""

    def __init__(self, model, background_data: np.ndarray, feature_names: List[str]):
        """
        Initialize SHAP explainer

        Args:
            model: Trained model (Isolation Forest)
            background_data: Background dataset for SHAP
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.Explainer(model.predict, background_data)
        logger.info(f"SHAP explainer initialized with {len(feature_names)} features")

    def explain(self, features: np.ndarray, top_k: int = 5) -> Dict[str, Any]:
        """
        Generate SHAP explanation for predictions

        Args:
            features: Feature array (scaled)
            top_k: Number of top features to return

        Returns:
            Dictionary with SHAP explanation details
        """
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)

            # Get feature importance (absolute SHAP values)
            feature_importance = {
                name: float(abs(value))
                for name, value in zip(self.feature_names, shap_values[0])
            }

            # Sort by importance
            sorted_features = sorted(
                feature_importance.items(), key=lambda x: x[1], reverse=True
            )

            # Get top contributing features
            top_features = dict(sorted_features[:top_k])

            # Build explanation
            explanation = {
                "top_contributing_features": top_features,
                "feature_values": {
                    name: float(value)
                    for name, value in zip(self.feature_names, features[0])
                },
                "shap_values": {
                    name: float(value)
                    for name, value in zip(self.feature_names, shap_values[0])
                },
            }

            return explanation

        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {str(e)}")
            # Return default explanation on error
            return {
                "top_contributing_features": {},
                "feature_values": {},
                "shap_values": {},
                "error": str(e),
            }

    def get_feature_importance_summary(
        self, features_batch: np.ndarray
    ) -> Dict[str, float]:
        """
        Get average feature importance across a batch

        Args:
            features_batch: Batch of feature arrays

        Returns:
            Dictionary of average feature importance
        """
        try:
            shap_values = self.explainer.shap_values(features_batch)

            # Calculate mean absolute SHAP values
            mean_importance = np.mean(np.abs(shap_values), axis=0)

            importance_dict = {
                name: float(value)
                for name, value in zip(self.feature_names, mean_importance)
            }

            return importance_dict

        except Exception as e:
            logger.error(f"Error calculating feature importance summary: {str(e)}")
            return {}

    def explain_prediction_difference(
        self, features_1: np.ndarray, features_2: np.ndarray
    ) -> Dict[str, Any]:
        """
        Explain the difference between two predictions

        Args:
            features_1: First feature array
            features_2: Second feature array

        Returns:
            Dictionary explaining the prediction difference
        """
        try:
            shap_1 = self.explainer.shap_values(features_1)[0]
            shap_2 = self.explainer.shap_values(features_2)[0]

            shap_diff = shap_1 - shap_2

            # Sort by absolute difference
            diff_importance = {
                name: float(abs(diff))
                for name, diff in zip(self.feature_names, shap_diff)
            }

            sorted_diffs = sorted(
                diff_importance.items(), key=lambda x: x[1], reverse=True
            )

            return {
                "most_different_features": dict(sorted_diffs[:5]),
                "shap_difference": {
                    name: float(diff)
                    for name, diff in zip(self.feature_names, shap_diff)
                },
                "feature_difference": {
                    name: float(features_1[0][i] - features_2[0][i])
                    for i, name in enumerate(self.feature_names)
                },
            }

        except Exception as e:
            logger.error(f"Error explaining prediction difference: {str(e)}")
            return {"error": str(e)}

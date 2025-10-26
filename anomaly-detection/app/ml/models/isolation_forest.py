from sklearn.ensemble import IsolationForest
import numpy as np

class IsolationForestDetector:
    def __init__(self, contamination=0.02, n_estimators=100, random_state=42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """Unsupervised training - no labels required"""
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X)
        self.is_fitted = True
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Return anomaly scores (lower is more anomalous)"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.score_samples(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predictions: -1 for anomalies, 1 for normal"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.predict(X)

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Return decision function scores"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.decision_function(X)


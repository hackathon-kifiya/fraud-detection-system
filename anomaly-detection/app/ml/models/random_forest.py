from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

class RandomForestAnomalyDetector:
    def __init__(self, n_estimators=100, random_state=42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Supervised training — requires labels y"""
        classes = np.unique(y)
        class_weights = compute_class_weight("balanced", classes=classes, y=y)
        class_weight_dict = dict(zip(classes, class_weights))
        
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            class_weight=class_weight_dict,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.predict_proba(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] > 0.5).astype(int)
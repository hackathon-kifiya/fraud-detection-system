"""
Training module for supervised and unsupervised models
"""

from app.ml.training.training_supervised import train_supervised_models
from app.ml.training.train_unsupervised import train_unsupervised_models

__all__ = [
    "train_supervised_models",
    "train_unsupervised_models",
]


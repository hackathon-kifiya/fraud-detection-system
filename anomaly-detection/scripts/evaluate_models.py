"""
Model Evaluation Script
Comprehensive evaluation of trained anomaly detection models
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score
)
import joblib  # noqa: E402
import argparse  # noqa: E402
from pathlib import Path  # noqa: E402
import json  # noqa: E402
from datetime import datetime  # noqa: E402

from app.core.config import settings  # noqa: E402


class ModelEvaluator:
    """Evaluate anomaly detection models"""

    def __init__(self, model_type: str):
        """
        Initialize evaluator

        Args:
            model_type: 'kyc', 'business', 'transaction', 'combined', or 'customer'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.results = {}

        # Load models
        self._load_models()

    def _load_models(self):
        """Load trained models"""
        models_dir = Path(settings.KYC_MODEL_PATH).parent

        if self.model_type == 'kyc':
            model_path = settings.KYC_MODEL_PATH
            scaler_path = settings.KYC_SCALER_PATH
        elif self.model_type == 'business':
            model_path = str(models_dir / 'business_model.pkl')
            scaler_path = str(models_dir / 'business_scaler.pkl')
        elif self.model_type == 'combined':
            model_path = str(models_dir / 'merged_model.pkl')
            scaler_path = str(models_dir / 'merged_scaler.pkl')
        elif self.model_type == 'customer':
            model_path = str(models_dir / 'customer_model.pkl')
            scaler_path = str(models_dir / 'customer_scaler.pkl')
        else:  # transaction
            model_path = settings.TRANSACTION_MODEL_PATH
            scaler_path = settings.TRANSACTION_SCALER_PATH

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Model files not found for {self.model_type}. Please train the model first.")

        print(f"Loading {self.model_type} model from: {model_path}")
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        print("Models loaded successfully!")

    def evaluate(self, X: np.ndarray, y_true: np.ndarray = None):
        """
        Evaluate model performance

        Args:
            X: Feature matrix
            y_true: True labels (1 for normal, -1 for anomaly), optional
        """
        print(f"\n{'='*60}")
        print(f"EVALUATING {self.model_type.upper()} MODEL")
        print(f"{'='*60}")

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Get predictions and scores
        y_pred = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)

        # Basic statistics
        self._compute_basic_stats(y_pred, scores)

        # If true labels provided, compute detailed metrics
        if y_true is not None:
            self._compute_classification_metrics(y_true, y_pred, scores)
            self._plot_confusion_matrix(y_true, y_pred)
            self._plot_roc_curve(y_true, scores)
            self._plot_precision_recall_curve(y_true, scores)

        # Distribution analysis
        self._plot_score_distribution(scores, y_pred, y_true)
        self._analyze_score_thresholds(scores, y_pred)

        return self.results

    def _compute_basic_stats(self, y_pred: np.ndarray, scores: np.ndarray):
        """Compute basic statistics"""
        print("\n--- Basic Statistics ---")

        total = len(y_pred)
        n_anomalies = np.sum(y_pred == -1)
        n_normal = np.sum(y_pred == 1)

        stats = {
            'total_samples': total,
            'predicted_normal': n_normal,
            'predicted_anomalies': n_anomalies,
            'anomaly_rate': (n_anomalies / total) * 100,
            'score_mean': scores.mean(),
            'score_std': scores.std(),
            'score_min': scores.min(),
            'score_max': scores.max(),
            'score_median': np.median(scores),
            'score_25th_percentile': np.percentile(scores, 25),
            'score_75th_percentile': np.percentile(scores, 75)
        }

        print(f"Total Samples: {total}")
        print(f"Predicted Normal: {n_normal} ({(n_normal/total)*100:.2f}%)")
        print(f"Predicted Anomalies: {n_anomalies} ({(n_anomalies/total)*100:.2f}%)")
        print("\nAnomaly Score Statistics:")
        print(f"  Mean: {stats['score_mean']:.4f}")
        print(f"  Std Dev: {stats['score_std']:.4f}")
        print(f"  Min: {stats['score_min']:.4f}")
        print(f"  Max: {stats['score_max']:.4f}")
        print(f"  Median: {stats['score_median']:.4f}")
        print(f"  25th Percentile: {stats['score_25th_percentile']:.4f}")
        print(f"  75th Percentile: {stats['score_75th_percentile']:.4f}")

        self.results['basic_stats'] = stats

    def _compute_classification_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, scores: np.ndarray):
        """Compute classification metrics"""
        print("\n--- Classification Metrics ---")

        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred, labels=[1, -1])
        tn, fp, fn, tp = cm.ravel()

        # Calculate metrics
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

        metrics = {
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'specificity': specificity
        }

        print(f"True Positives (Anomalies detected): {tp}")
        print(f"True Negatives (Normal detected): {tn}")
        print(f"False Positives (Normal flagged as anomaly): {fp}")
        print(f"False Negatives (Anomalies missed): {fn}")
        print(f"\nAccuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall (Sensitivity): {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print(f"Specificity: {specificity:.4f}")

        # Detailed classification report
        print("\n--- Detailed Classification Report ---")
        target_names = ['Normal', 'Anomaly']
        report = classification_report(y_true, y_pred, labels=[1, -1], target_names=target_names)
        print(report)

        self.results['classification_metrics'] = metrics
        self.results['classification_report'] = report

    def _plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred, labels=[1, -1])

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Normal', 'Anomaly'],
                    yticklabels=['Normal', 'Anomaly'])
        plt.title(f'Confusion Matrix - {self.model_type.upper()} Model')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')

        output_path = f'outputs/{self.model_type}_confusion_matrix.png'
        os.makedirs('outputs', exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nConfusion matrix saved to: {output_path}")
        plt.close()

    def _plot_roc_curve(self, y_true: np.ndarray, scores: np.ndarray):
        """Plot ROC curve"""
        # Convert predictions to binary (1 for anomaly, 0 for normal)
        y_true_binary = (y_true == -1).astype(int)

        # Scores are negative for anomalies, so we negate them
        fpr, tpr, thresholds = roc_curve(y_true_binary, -scores)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(10, 8))
        plt.plot(fpr, tpr, color='darkorange', lw=2,
                label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {self.model_type.upper()} Model')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)

        output_path = f'outputs/{self.model_type}_roc_curve.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"ROC curve saved to: {output_path}")
        plt.close()

        self.results['roc_auc'] = roc_auc

    def _plot_precision_recall_curve(self, y_true: np.ndarray, scores: np.ndarray):
        """Plot Precision-Recall curve"""
        y_true_binary = (y_true == -1).astype(int)

        precision, recall, thresholds = precision_recall_curve(y_true_binary, -scores)
        avg_precision = average_precision_score(y_true_binary, -scores)

        plt.figure(figsize=(10, 8))
        plt.plot(recall, precision, color='blue', lw=2,
                label=f'PR curve (AP = {avg_precision:.4f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - {self.model_type.upper()} Model')
        plt.legend(loc="lower left")
        plt.grid(alpha=0.3)

        output_path = f'outputs/{self.model_type}_precision_recall_curve.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Precision-Recall curve saved to: {output_path}")
        plt.close()

        self.results['average_precision'] = avg_precision

    def _plot_score_distribution(self, scores: np.ndarray, y_pred: np.ndarray, y_true: np.ndarray = None):
        """Plot anomaly score distribution"""
        plt.figure(figsize=(12, 6))

        if y_true is not None:
            # Plot by true labels
            normal_scores = scores[y_true == 1]
            anomaly_scores = scores[y_true == -1]

            plt.hist(normal_scores, bins=50, alpha=0.5, label='True Normal', color='green')
            plt.hist(anomaly_scores, bins=50, alpha=0.5, label='True Anomaly', color='red')
        else:
            # Plot by predicted labels
            normal_scores = scores[y_pred == 1]
            anomaly_scores = scores[y_pred == -1]

            plt.hist(normal_scores, bins=50, alpha=0.5, label='Predicted Normal', color='blue')
            plt.hist(anomaly_scores, bins=50, alpha=0.5, label='Predicted Anomaly', color='orange')

        plt.xlabel('Anomaly Score')
        plt.ylabel('Frequency')
        plt.title(f'Anomaly Score Distribution - {self.model_type.upper()} Model')
        plt.legend()
        plt.grid(alpha=0.3)

        # Add threshold lines
        plt.axvline(settings.HIGH_RISK_THRESHOLD, color='red', linestyle='--',
                   label=f'High Risk ({settings.HIGH_RISK_THRESHOLD})')
        plt.axvline(settings.MEDIUM_RISK_THRESHOLD, color='orange', linestyle='--',
                   label=f'Medium Risk ({settings.MEDIUM_RISK_THRESHOLD})')
        plt.legend()

        output_path = f'outputs/{self.model_type}_score_distribution.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Score distribution saved to: {output_path}")
        plt.close()

    def _analyze_score_thresholds(self, scores: np.ndarray, y_pred: np.ndarray):
        """Analyze different threshold levels"""
        print("\n--- Threshold Analysis ---")

        high_risk = np.sum(scores < settings.HIGH_RISK_THRESHOLD)
        medium_risk = np.sum((scores >= settings.HIGH_RISK_THRESHOLD) &
                            (scores < settings.MEDIUM_RISK_THRESHOLD))
        low_risk = np.sum(scores >= settings.MEDIUM_RISK_THRESHOLD)

        total = len(scores)

        threshold_stats = {
            'high_risk_count': int(high_risk),
            'medium_risk_count': int(medium_risk),
            'low_risk_count': int(low_risk),
            'high_risk_percentage': (high_risk / total) * 100,
            'medium_risk_percentage': (medium_risk / total) * 100,
            'low_risk_percentage': (low_risk / total) * 100
        }

        print(f"High Risk (score < {settings.HIGH_RISK_THRESHOLD}): {high_risk} ({threshold_stats['high_risk_percentage']:.2f}%)")
        print(f"Medium Risk ({settings.HIGH_RISK_THRESHOLD} ≤ score < {settings.MEDIUM_RISK_THRESHOLD}): {medium_risk} ({threshold_stats['medium_risk_percentage']:.2f}%)")
        print(f"Low Risk (score ≥ {settings.MEDIUM_RISK_THRESHOLD}): {low_risk} ({threshold_stats['low_risk_percentage']:.2f}%)")

        self.results['threshold_analysis'] = threshold_stats

    def save_results(self, output_dir: str = 'outputs'):
        """Save evaluation results to JSON"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f'{self.model_type}_evaluation_{timestamp}.json')

        # Convert numpy types to native Python types
        results_json = json.loads(json.dumps(self.results, default=str))

        with open(output_path, 'w') as f:
            json.dump(results_json, f, indent=2)

        print(f"\nEvaluation results saved to: {output_path}")


def prepare_kyc_features(df: pd.DataFrame) -> np.ndarray:
    """Extract KYC features - matches training script exactly"""
    features = []

    features.append(df['customer_age'].values)
    gender_encoded = (df['customer_gender'] == 'female').astype(int)
    features.append(gender_encoded.values)

    marital_mapping = {'single': 0, 'married': 1, 'divorced': 2, 'widowed': 3}
    marital_encoded = df['customer_marital_status'].map(marital_mapping).fillna(-1)
    features.append(marital_encoded.values)

    education_mapping = {'primary': 0, 'secondary': 1, 'tertiary': 2, 'post_graduate': 3}
    education_encoded = df['customer_education_level'].map(education_mapping).fillna(-1)
    features.append(education_encoded.values)

    region_encoded = pd.Categorical(df['customer_region']).codes
    features.append(region_encoded)

    city_encoded = pd.Categorical(df['customer_city']).codes
    features.append(city_encoded)

    zone_encoded = pd.Categorical(df['customer_zone_or_sub_city']).codes
    features.append(zone_encoded)

    woreda_numeric = pd.to_numeric(df['customer_woreda'], errors='coerce').fillna(0)
    features.append(woreda_numeric.values)

    phone_last_4 = df['customer_phone_number'].astype(str).str[-4:].astype(int)
    features.append(phone_last_4.values)

    tin_length = df['customer_tin_number'].str.len()
    features.append(tin_length.values)

    account_length = df['customer_bank_account_number'].str.len()
    features.append(account_length.values)

    return np.column_stack(features)


def prepare_business_features(df: pd.DataFrame) -> np.ndarray:
    """Extract business features - matches training script exactly"""
    features = []

    features.append(df['business_establishment_year'].values)

    sector_mapping = {
        'AGRICULTURE': 0, 'MANUFACTURING': 1, 'DOMESTIC_TRADE_SERVICES': 2,
        'SERVICES': 3, 'OTHER': 4
    }
    sector_encoded = df['business_sector'].map(sector_mapping).fillna(-1)
    features.append(sector_encoded.values)

    level_mapping = {'GROWING': 0, 'STARTUP': 1}
    level_encoded = df['business_level'].map(level_mapping).fillna(-1)
    features.append(level_encoded.values)

    features.append(df['business_starting_capital'].values)
    features.append(df['business_current_capital'].values)
    features.append(df['business_annual_profit'].values)
    features.append(df['business_annual_sales'].values)
    features.append(df['business_starting_no_of_employees'].values)
    features.append(df['business_current_no_of_employees'].values)

    source_mapping = {'FAMILY': 0, 'OWN': 1, 'LOAN': 2, 'FUND': 3, 'OTHER': 4}
    source_encoded = df['business_source_of_initial_capital'].map(source_mapping).fillna(-1)
    features.append(source_encoded.values)

    association_mapping = {
        'SOLE_PROPRIETORSHIP': 0, 'PARTNERSHIP': 1, 'CORPORATION': 2, 'OTHER': 3
    }
    association_encoded = df['business_association_type'].map(association_mapping).fillna(-1)
    features.append(association_encoded.values)

    capital_growth = np.where(df['business_starting_capital'] > 0,
                             df['business_current_capital'] / df['business_starting_capital'], 0)
    features.append(capital_growth)

    employee_growth = np.where(df['business_starting_no_of_employees'] > 0,
                              df['business_current_no_of_employees'] / df['business_starting_no_of_employees'], 0)
    features.append(employee_growth)

    profit_margin = np.where(df['business_annual_sales'] > 0,
                            df['business_annual_profit'] / df['business_annual_sales'], 0)
    features.append(profit_margin)

    current_year = 2024
    business_age = current_year - df['business_establishment_year']
    features.append(business_age.values)

    return np.column_stack(features)


def prepare_transaction_features(df: pd.DataFrame) -> np.ndarray:
    """Extract transaction features"""
    type_mapping = {'purchase': 0, 'withdrawal': 1, 'transfer': 2, 'deposit': 3}
    df['transaction_type_encoded'] = df['transaction_type'].map(type_mapping)

    features = df[[
        'amount', 'transaction_type_encoded', 'hour_of_day', 'day_of_week',
        'distance_from_home', 'is_online', 'num_transactions_last_24h',
        'avg_amount_last_30d'
    ]].values
    return features


def prepare_customer_features(df: pd.DataFrame) -> np.ndarray:
    """Extract customer features (KYC + Business combined)"""
    kyc_features = prepare_kyc_features(df)
    business_features = prepare_business_features(df)
    return np.column_stack([kyc_features, business_features])


def prepare_combined_features(df: pd.DataFrame) -> np.ndarray:
    """Extract combined features (KYC + Business + Transaction)"""
    kyc_features = prepare_kyc_features(df)
    business_features = prepare_business_features(df)
    transaction_features = prepare_transaction_features(df)
    return np.column_stack([kyc_features, business_features, transaction_features])


def generate_synthetic_kyc_data(n_samples: int = 5000) -> np.ndarray:
    """Generate synthetic KYC data matching training format"""
    # Generate realistic synthetic KYC data
    data = {
        'customer_age': np.random.randint(18, 80, n_samples),
        'customer_gender': np.random.choice(['male', 'female'], n_samples),
        'customer_marital_status': np.random.choice(['single', 'married', 'divorced', 'widowed'], n_samples),
        'customer_education_level': np.random.choice(['primary', 'secondary', 'tertiary', 'post_graduate'], n_samples),
        'customer_region': np.random.choice(['Addis Ababa', 'Oromia', 'Amhara', 'Tigray', 'SNNPR'], n_samples),
        'customer_city': np.random.choice(['Addis Ababa', 'Dire Dawa', 'Mekelle', 'Bahir Dar', 'Awasa'], n_samples),
        'customer_zone_or_sub_city': np.random.choice(['Zone1', 'Zone2', 'Zone3', 'Zone4'], n_samples),
        'customer_woreda': np.random.randint(1, 20, n_samples).astype(str),
        'customer_phone_number': ['09' + str(np.random.randint(10000000, 99999999)) for _ in range(n_samples)],
        'customer_tin_number': ['TIN' + str(np.random.randint(1000000, 9999999)) for _ in range(n_samples)],
        'customer_bank_account_number': ['ACC' + str(np.random.randint(100000000, 999999999)) for _ in range(n_samples)],
    }
    df = pd.DataFrame(data)
    return prepare_kyc_features(df)


def generate_synthetic_business_data(n_samples: int = 5000) -> np.ndarray:
    """Generate synthetic business data matching training format"""
    current_year = 2024
    data = {
        'business_establishment_year': np.random.randint(1990, 2024, n_samples),
        'business_sector': np.random.choice(['AGRICULTURE', 'MANUFACTURING', 'DOMESTIC_TRADE_SERVICES', 'SERVICES', 'OTHER'], n_samples),
        'business_level': np.random.choice(['GROWING', 'STARTUP'], n_samples),
        'business_starting_capital': np.random.uniform(10000, 500000, n_samples),
        'business_current_capital': np.random.uniform(10000, 1000000, n_samples),
        'business_annual_profit': np.random.uniform(-50000, 300000, n_samples),
        'business_annual_sales': np.random.uniform(50000, 1000000, n_samples),
        'business_starting_no_of_employees': np.random.randint(1, 20, n_samples),
        'business_current_no_of_employees': np.random.randint(1, 50, n_samples),
        'business_source_of_initial_capital': np.random.choice(['FAMILY', 'OWN', 'LOAN', 'FUND', 'OTHER'], n_samples),
        'business_association_type': np.random.choice(['SOLE_PROPRIETORSHIP', 'PARTNERSHIP', 'CORPORATION', 'OTHER'], n_samples),
    }
    df = pd.DataFrame(data)
    return prepare_business_features(df)


def generate_synthetic_transaction_data(n_samples: int = 5000) -> np.ndarray:
    """Generate synthetic transaction data matching training format"""
    data = {
        'amount': np.random.uniform(10, 10000, n_samples),
        'transaction_type': np.random.choice(['purchase', 'withdrawal', 'transfer', 'deposit'], n_samples),
        'hour_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'distance_from_home': np.random.uniform(0, 100, n_samples),
        'is_online': np.random.choice([0, 1], n_samples),
        'num_transactions_last_24h': np.random.randint(0, 20, n_samples),
        'avg_amount_last_30d': np.random.uniform(50, 5000, n_samples),
    }
    df = pd.DataFrame(data)
    return prepare_transaction_features(df)


def generate_synthetic_customer_data(n_samples: int = 5000) -> np.ndarray:
    """Generate synthetic customer data (KYC + Business)"""
    kyc_features = generate_synthetic_kyc_data(n_samples)
    business_features = generate_synthetic_business_data(n_samples)
    return np.column_stack([kyc_features, business_features])


def generate_synthetic_combined_data(n_samples: int = 5000) -> np.ndarray:
    """Generate synthetic combined data (KYC + Business + Transaction)"""
    kyc_features = generate_synthetic_kyc_data(n_samples)
    business_features = generate_synthetic_business_data(n_samples)
    transaction_features = generate_synthetic_transaction_data(n_samples)
    return np.column_stack([kyc_features, business_features, transaction_features])


def main():
    parser = argparse.ArgumentParser(description='Evaluate anomaly detection models')
    parser.add_argument('--model-type', type=str, required=True,
                       choices=['kyc', 'business', 'transaction', 'customer', 'combined', 'all'],
                       help='Model type to evaluate')
    parser.add_argument('--test-data', type=str, help='Path to test data CSV')
    parser.add_argument('--labels-col', type=str, default='is_anomaly',
                       help='Column name for true labels')
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Output directory for results')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    # Determine which models to evaluate
    if args.model_type == 'all':
        models_to_evaluate = ['kyc', 'business', 'transaction', 'customer', 'combined']
    else:
        models_to_evaluate = [args.model_type]

    for model_type in models_to_evaluate:
        try:
            evaluator = ModelEvaluator(model_type)

            if args.test_data:
                # Load test data
                print(f"\nLoading test data from: {args.test_data}")
                df = pd.read_csv(args.test_data)

                # Prepare features based on model type
                if model_type == 'kyc':
                    X = prepare_kyc_features(df)
                elif model_type == 'business':
                    X = prepare_business_features(df)
                elif model_type == 'transaction':
                    X = prepare_transaction_features(df)
                elif model_type == 'customer':
                    X = prepare_customer_features(df)
                elif model_type == 'combined':
                    X = prepare_combined_features(df)

                # Get true labels if available
                y_true = None
                if args.labels_col in df.columns:
                    # Convert to Isolation Forest format (1 for normal, -1 for anomaly)
                    y_true = df[args.labels_col].apply(lambda x: -1 if x == 1 else 1).values

                # Evaluate
                evaluator.evaluate(X, y_true)
            else:
                print("\nNo test data provided. Generating synthetic data for evaluation...")
                # Generate synthetic data matching training format
                if model_type == 'kyc':
                    X = generate_synthetic_kyc_data(5000)
                elif model_type == 'business':
                    X = generate_synthetic_business_data(5000)
                elif model_type == 'transaction':
                    X = generate_synthetic_transaction_data(5000)
                elif model_type == 'customer':
                    X = generate_synthetic_customer_data(5000)
                elif model_type == 'combined':
                    X = generate_synthetic_combined_data(5000)
                else:
                    print(f"Unknown model type: {model_type}. Skipping...")
                    continue

                evaluator.evaluate(X)

            # Save results
            evaluator.save_results(args.output_dir)

        except FileNotFoundError as e:
            print(f"\n⚠ Skipping {model_type} model: {e}")
            continue
        except Exception as e:
            print(f"\n❌ Error evaluating {model_type} model: {e}")
            continue

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE!")
    print("=" * 60)
    print(f"\nResults saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()
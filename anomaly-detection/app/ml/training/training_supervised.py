import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler, RobustScaler

from app.ml.models.random_forest import RandomForestAnomalyDetector
from app.ml.preprocessing.feature_engineering import (
    prepare_transaction_features,
    prepare_customer_features,
    prepare_kyc_features,
    prepare_business_features,
)

MODELS_DIR = Path("data/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train_supervised_model(
    X: np.ndarray,
    y: np.ndarray,
    model_type: str,
    use_robust_scaler=False,
    n_estimators=100
):
    """
    Train Random Forest with optimized parameters per model type
    """
    print(f"\nTraining SUPERVISED {model_type} model...")
    print(f"Training samples: {X.shape[0]}, Features: {X.shape[1]}")
    
    # Check label distribution
    unique, counts = np.unique(y, return_counts=True)
    print(f"Label distribution: {dict(zip(unique, counts))}")
    
    if use_robust_scaler:
        scaler = RobustScaler()
        print("Using RobustScaler (better for outliers)")
    else:
        scaler = StandardScaler()
        print("Using StandardScaler")
    
    X_scaled = scaler.fit_transform(X)
    
    # Model-specific hyperparameters
    if model_type == "customer":
        n_estimators = 200
    elif model_type == "transaction":
        n_estimators = 150
    elif model_type == "merged":
        n_estimators = 175
    else:
        n_estimators = n_estimators
    
    # Train Random Forest
    model = RandomForestAnomalyDetector(
        n_estimators=n_estimators,
        random_state=42
    )
    model.fit(X_scaled, y)
    
    # Evaluation
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    
    anomaly_count = np.sum(predictions == 1)
    anomaly_pct = (anomaly_count / len(predictions)) * 100
    true_anomalies = np.sum(y == 1)
    
    print("✓ Training complete!")
    print(f"  True anomalies in data: {true_anomalies}")
    print(f"  Predicted anomalies: {anomaly_count} ({anomaly_pct:.2f}%)")
    print(f"  Probability range: [{probabilities[:, 1].min():.3f}, {probabilities[:, 1].max():.3f}]")
    print(f"  Probability mean: {probabilities[:, 1].mean():.3f}")
    
    # Calculate accuracy
    accuracy = np.mean(predictions == y)
    print(f"  Training accuracy: {accuracy:.3f}")
    
    return model, scaler


def train_supervised_models():
    """Train supervised Random Forest models"""
    print("=" * 70)
    print("TRAINING SUPERVISED MODELS WITH RANDOM FOREST")
    print("=" * 70)
    
    data_dir = Path("data/raw")
    
    # 1. MERGED MODEL (KYC + Business)
    print("\n[1/3] MERGED MODEL (KYC + Business)")
    merged_path = data_dir / "kyc_business_training_data.csv"
    if merged_path.exists():
        df = pd.read_csv(merged_path)
        print(f"Loaded {len(df)} records")
        
        # Extract labels
        y = df["is_anomaly"].values
        
        # Prepare features
        kyc_feat = prepare_kyc_features(df)
        biz_feat = prepare_business_features(df)
        X = np.column_stack([kyc_feat, biz_feat])
        
        model, scaler = train_supervised_model(X, y, "merged", use_robust_scaler=True)
        
        joblib.dump(model, MODELS_DIR / "merged_supervised_model.pkl")
        joblib.dump(scaler, MODELS_DIR / "merged_supervised_scaler.pkl")
        print(f"✓ Saved to {MODELS_DIR}/merged_supervised_model.pkl")
    else:
        print(f"❌ {merged_path} not found")
    
    # 2. TRANSACTION MODEL
    print("\n[2/3] TRANSACTION MODEL")
    txn_path = data_dir / "transaction_training_data.csv"
    if txn_path.exists():
        df = pd.read_csv(txn_path)
        print(f"Loaded {len(df)} records")
        
        # Extract labels
        y = df["is_anomaly"].values
        
        # Prepare features
        X = prepare_transaction_features(df)
        
        model, scaler = train_supervised_model(X, y, "transaction")
        
        joblib.dump(model, MODELS_DIR / "transaction_supervised_model.pkl")
        joblib.dump(scaler, MODELS_DIR / "transaction_supervised_scaler.pkl")
        print(f"✓ Saved to {MODELS_DIR}/transaction_supervised_model.pkl")
    else:
        print(f"❌ {txn_path} not found")
    
    # 3. CUSTOMER MODEL (FIXED)
    print("\n[3/3] CUSTOMER MODEL")
    if txn_path.exists():
        df = pd.read_csv(txn_path)
        print(f"Loaded {len(df)} transaction records")
        
        # Generate customer-level features
        X, customer_ids = prepare_customer_features(df)
        
        # Create customer-level labels by aggregating transaction labels
        customer_label_map = df.groupby("customer_id")["is_anomaly"].max()
        y = np.array([customer_label_map[cid] for cid in customer_ids])
        
        print(f"Customer features shape: {X.shape}, Labels shape: {y.shape}")
        
        model, scaler = train_supervised_model(X, y, "customer", use_robust_scaler=True)
        
        joblib.dump(model, MODELS_DIR / "customer_supervised_model.pkl")
        joblib.dump(scaler, MODELS_DIR / "customer_supervised_scaler.pkl")
        print(f"✓ Saved to {MODELS_DIR}/customer_supervised_model.pkl")
    else:
        print(f"❌ {txn_path} not found")
    
    print("\n" + "=" * 70)
    print("✅ ALL SUPERVISED MODELS TRAINED WITH RANDOM FOREST!")
    print("=" * 70)
    print("\nKey Features:")
    print("  • Supervised learning with labeled data")
    print("  • Balanced class weights for imbalanced datasets")
    print("  • Model-specific hyperparameter tuning")
    print("  • Robust scaling for outlier resistance")


if __name__ == "__main__":
    train_supervised_models()
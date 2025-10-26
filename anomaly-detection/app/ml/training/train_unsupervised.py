import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, RobustScaler

from app.ml.preprocessing.feature_engineering import (
    prepare_transaction_features,
    prepare_customer_features,
    prepare_kyc_features,
    prepare_business_features,
)

MODELS_DIR = Path("data/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def train_unsupervised_model(X: np.ndarray, model_type: str, use_robust_scaler=False):
    """
    Train Isolation Forest with optimized parameters per model type
    """
    print(f"\nTraining OPTIMIZED {model_type} model...")
    print(f"Training samples: {X.shape[0]}, Features: {X.shape[1]}")
    
    if use_robust_scaler:
        scaler = RobustScaler() 
        print("Using RobustScaler (better for outliers)")
    else:
        scaler = StandardScaler()
        print("Using StandardScaler")
    
    X_scaled = scaler.fit_transform(X)
    
    if model_type == "customer":
        model = IsolationForest(
            contamination=0.015,  
            n_estimators=200,
            max_samples=min(512, X.shape[0]),
            max_features=min(15, X.shape[1]),
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
    elif model_type == "transaction":
        model = IsolationForest(
            contamination=0.02,
            n_estimators=150,
            max_samples=2048,
            max_features=0.8, 
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
    elif model_type == "merged":
        model = IsolationForest(
            contamination=0.02,
            n_estimators=175,
            max_samples=1024,
            max_features=0.7,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
    else:
        model = IsolationForest(
            contamination=0.02,
            n_estimators=100,
            max_samples=min(2048, X.shape[0]),
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
    
    model.fit(X_scaled)
    
    predictions = model.predict(X_scaled)
    scores = model.score_samples(X_scaled)
    
    anomaly_count = np.sum(predictions == -1)
    anomaly_pct = (anomaly_count / len(predictions)) * 100
    
    print("✓ Training complete!")
    print(f"  Anomalies detected: {anomaly_count} ({anomaly_pct:.2f}%)")
    print(f"  Score range: [{scores.min():.3f}, {scores.max():.3f}]")
    print(f"  Score mean: {scores.mean():.3f}, std: {scores.std():.3f}")
    
    return model, scaler, scores

def train_unsupervised_models():
    print("=" * 70)
    print("TRAINING MODELS")
    print("=" * 70)
    
    data_dir = Path("data/raw")
    
    # 1. MERGED MODEL (KYC + Business)
    print("\n[1/3] MERGED MODEL (KYC + Business)")
    merged_path = data_dir / "kyc_business_training_data.csv"
    if merged_path.exists():
        df = pd.read_csv(merged_path)
        print(f"Loaded {len(df)} records")
        
        kyc_feat = prepare_kyc_features(df)
        biz_feat = prepare_business_features(df)
        X = np.column_stack([kyc_feat, biz_feat])
        
        model, scaler, _ = train_unsupervised_model(X, "merged", use_robust_scaler=True)
        
        joblib.dump(model, MODELS_DIR / "merged_model.pkl")
        joblib.dump(scaler, MODELS_DIR / "merged_scaler.pkl")
        print(f"✓ Saved to {MODELS_DIR}/merged_model.pkl")
    else:
        print(f"❌ {merged_path} not found")
    
    # 2. TRANSACTION MODEL
    print("\n[2/3] TRANSACTION MODEL")
    txn_path = data_dir / "transaction_training_data.csv"
    if txn_path.exists():
        df = pd.read_csv(txn_path)
        print(f"Loaded {len(df)} records")
        
        X = prepare_transaction_features(df)
        model, scaler, _ = train_unsupervised_model(X, "transaction")
        
        joblib.dump(model, MODELS_DIR / "transaction_model.pkl")
        joblib.dump(scaler, MODELS_DIR / "transaction_scaler.pkl")
        print(f"✓ Saved to {MODELS_DIR}/transaction_model.pkl")
    else:
        print(f"❌ {txn_path} not found")
    
    # 3. CUSTOMER MODEL
    print("\n[3/3] CUSTOMER MODEL")
    if txn_path.exists():
        df = pd.read_csv(txn_path)
        print(f"Loaded {len(df)} transaction records")
        
        X, customer_ids = prepare_customer_features(df)
        model, scaler, _ = train_unsupervised_model(X, "customer", use_robust_scaler=True)
        
        joblib.dump(model, MODELS_DIR / "customer_model.pkl")
        joblib.dump(scaler, MODELS_DIR / "customer_scaler.pkl")
        print(f"✓ Saved to {MODELS_DIR}/customer_model.pkl")
    else:
        print(f"❌ {txn_path} not found")
    
    print("\n" + "=" * 70)
    print("✅ ALL MAIN MODELS TRAINED WITH ENHANCED FEATURES!")
    print("=" * 70)
    print("\nKey Improvements:")
    print("  • Enhanced feature engineering (financial ratios, patterns)")
    print("  • Model-specific hyperparameter tuning")
    print("  • Robust scaling for outlier resistance")
    print("  • Advanced behavioral indicators")


if __name__ == "__main__":
    train_unsupervised_models()
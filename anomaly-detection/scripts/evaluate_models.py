import json
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path

# Model paths
MODEL_CONFIG = {
    "kyc": {
        "model_path": "data/models/kyc_model.pkl",
        "scaler_path": "data/models/kyc_scaler.pkl",
        "data_path": "data/evaluation/kyc_evaluation_data.csv",
        "id_col": "customerId"
    },
    "business": {
        "model_path": "data/models/business_model.pkl",
        "scaler_path": "data/models/business_scaler.pkl",
        "data_path": "data/evaluation/business_evaluation_data.csv",
        "id_col": "customerId"
    },
    "transaction": {
        "model_path": "data/models/transaction_model.pkl",
        "scaler_path": "data/models/transaction_scaler.pkl",
        "data_path": "data/evaluation/transaction_evaluation_data.csv",
        "id_col": "customer_id"
    },
    "merged": {
        "model_path": "data/models/merged_model.pkl",
        "scaler_path": "data/models/merged_scaler.pkl",
        "data_path": "data/evaluation/kyc_business_evaluation_data.csv",
        "id_col": "customerId"
    },
    "customer": {
        "model_path": "data/models/customer_model.pkl",
        "scaler_path": "data/models/customer_scaler.pkl",
        "data_path": "data/evaluation/transaction_evaluation_data.csv",
        "id_col": None  # Will use customer_id from aggregation
    }
}

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# CONTAMINATION used during training (must match!)
CONTAMINATION = 0.02


def prepare_transaction_features(df: pd.DataFrame) -> np.ndarray:
    """Enhanced transaction features with velocity and pattern detection"""
    features = []
    df = df.copy()
    
    # Basic amounts
    credit = df["credit"].values
    debit = df["debit"].values
    balance = df["closingBalance"].values
    
    features.extend([credit, debit, balance])
    features.extend([np.log1p(credit), np.log1p(debit), np.log1p(balance)])
    
    # Source encoding
    source_mapping = {
        "cash deposit": 0, 
        "fund transfer": 1, 
        "cash withdraw": 2,
        "tele birr incoming": 3, 
        "tele birr out going": 4, 
        "atm card subscription fee": 5
    }
    source_encoded = df["source"].str.lower().map(source_mapping).fillna(-1).values
    features.append(source_encoded)
    
    # Narrative analysis
    narrative_length = df["narrative"].fillna("").str.len().values
    features.append(narrative_length)
    
    # Transaction amount (net) - already numpy arrays
    transaction_amount = credit - debit
    features.append(transaction_amount)
    features.append(np.abs(transaction_amount))
    
    # Balance ratio
    balance_ratio = np.where(balance > 0, transaction_amount / balance, 0)
    features.append(np.clip(balance_ratio, -10, 10))
    
    # Date features
    df["date"] = pd.to_datetime(df["date"])
    hour = df["date"].dt.hour.values
    dayofweek = df["date"].dt.dayofweek.values
    day = df["date"].dt.day.values
    month = df["date"].dt.month.values
    
    features.extend([hour, dayofweek, day, month])
    
    # NEW: Time-based anomaly indicators
    is_night = ((hour >= 22) | (hour <= 6)).astype(int)
    is_weekend = (dayofweek >= 5).astype(int)
    features.extend([is_night, is_weekend])
    
    # Customer transaction frequency
    customer_txn_counts = df.groupby("customer_id").size()
    txn_freq = df["customer_id"].map(customer_txn_counts).values
    features.append(txn_freq)
    
    # NEW: Round amount detection (fraud indicator)
    is_round = ((credit % 1000 == 0) | (debit % 1000 == 0)).astype(int)
    features.append(is_round)
    
    # NEW: Customer-level velocity (within-day transactions)
    df["date_only"] = df["date"].dt.date
    daily_txn_count = df.groupby(["customer_id", "date_only"]).size()
    df["daily_velocity"] = df.set_index(["customer_id", "date_only"]).index.map(daily_txn_count.to_dict())
    daily_velocity = df["daily_velocity"].fillna(1).values
    features.append(daily_velocity)
    
    return np.column_stack(features)


def prepare_customer_features(df: pd.DataFrame) -> tuple[np.ndarray, list]:
    """Prepare customer-level features with advanced behavior patterns"""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    
    customer_ids = []
    customer_features = []
    
    for customer_id, group in df.groupby("customer_id"):
        customer_ids.append(customer_id)
        n_txns = len(group)
        features = []
        
        # Basic volume metrics
        features.append(n_txns)
        features.append(np.log1p(n_txns))
        
        # Amount statistics
        credit_sum = group["credit"].sum()
        debit_sum = group["debit"].sum()
        features.extend([
            credit_sum, debit_sum,
            group["credit"].mean(), group["debit"].mean(),
            group["credit"].max(), group["debit"].max(),
            group["credit"].std() if n_txns > 1 else 0.0,
            group["debit"].std() if n_txns > 1 else 0.0
        ])
        
        # NEW: Credit/Debit ratio
        cd_ratio = credit_sum / (debit_sum + 1)
        features.append(np.log1p(cd_ratio))
        
        # Balance statistics
        balance = group["closingBalance"]
        features.extend([
            balance.mean(), balance.max(), balance.min(),
            balance.std() if n_txns > 1 else 0.0
        ])
        
        # Transaction amount stats
        txn_amt = group["credit"] - group["debit"]
        features.extend([
            txn_amt.mean(), txn_amt.max(), txn_amt.min(),
            txn_amt.std() if n_txns > 1 else 0.0,
            txn_amt.median()
        ])
        
        # Source diversity
        total = max(n_txns, 1)
        source_counts = group["source"].value_counts()
        features.extend([
            len(source_counts),  # Diversity
            source_counts.iloc[0] / total if len(source_counts) > 0 else 0.0,  # Dominance
            (group["source"].str.contains("CASH DEPOSIT", case=False, na=False)).sum() / total,
            (group["source"].str.contains("FUND TRANSFER", case=False, na=False)).sum() / total,
            (group["source"].str.contains("CASH WITHDRAW", case=False, na=False)).sum() / total,
            (group["source"].str.contains("TELE BIRR", case=False, na=False)).sum() / total
        ])
        
        # Temporal patterns
        hours = group["date"].dt.hour
        features.extend([
            hours.mean(),
            hours.std() if n_txns > 1 else 0.0,
            ((hours >= 22) | (hours <= 6)).sum() / total,  # Night transactions
            ((hours >= 9) & (hours <= 17)).sum() / total   # Business hours
        ])
        
        dow = group["date"].dt.dayofweek
        features.extend([
            (dow < 5).sum() / total,    # Weekday ratio
            (dow >= 5).sum() / total    # Weekend ratio
        ])
        
        # Time between transactions (velocity)
        if n_txns > 1:
            sorted_dates = group["date"].sort_values()
            diffs_hours = sorted_dates.diff().dt.total_seconds().fillna(0) / 3600
            features.extend([
                diffs_hours.mean(),
                diffs_hours.median(),
                diffs_hours.min(),
                diffs_hours.max(),
                diffs_hours.std()
            ])
            
            # NEW: Burst detection (many transactions in short time)
            rapid_txns = (diffs_hours < 1).sum()
            features.append(rapid_txns / max(n_txns - 1, 1))
        else:
            features.extend([0.0] * 6)
        
        # Narrative patterns
        narratives = group["narrative"].fillna("")
        features.extend([
            narratives.str.len().mean(),
            narratives.nunique(),
            narratives.nunique() / total,  # Diversity
            (narratives.str.len() < 5).sum() / total  # Short narratives
        ])
        
        # Balance behavior
        balance_ratio = np.where(balance > 0, txn_amt / balance, 0)
        features.extend([
            np.mean(balance_ratio),
            np.max(balance_ratio),
            np.std(balance_ratio) if n_txns > 1 else 0.0
        ])
        
        # Risk indicators
        high_amt_thresh = txn_amt.quantile(0.9) if n_txns > 0 else 0
        high_amt_ratio = (np.abs(txn_amt) > high_amt_thresh).sum() / total
        features.append(high_amt_ratio)
        
        # NEW: Round amount ratio (fraud indicator)
        round_amt_ratio = ((group["credit"] % 1000 == 0) | (group["debit"] % 1000 == 0)).sum() / total
        features.append(round_amt_ratio)
        
        # NEW: Account lifetime (days active)
        account_lifetime = (group["date"].max() - group["date"].min()).days
        features.append(account_lifetime)
        
        # NEW: Activity intensity (txns per day active)
        activity_intensity = n_txns / max(account_lifetime, 1)
        features.append(activity_intensity)
        
        # Ensure all features are float
        features = [float(x) if pd.notna(x) else 0.0 for x in features]
        customer_features.append(features)
    
    X = np.array(customer_features, dtype=np.float32)
    print(f"Generated {X.shape[1]} features for {len(customer_ids)} customers")
    return X, customer_ids




# ======================
# EVALUATION FUNCTIONS
# ======================

def plot_precision_recall_curve(y_true, anomaly_scores, model_name):
    from sklearn.metrics import precision_recall_curve, average_precision_score
    precision, recall, thresholds = precision_recall_curve(y_true, anomaly_scores)
    pr_auc = average_precision_score(y_true, anomaly_scores)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, marker='.', label=f'PR AUC = {pr_auc:.3f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'{model_name.title()} Precision-Recall Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig(OUTPUT_DIR / f"{model_name}_precision_recall_curve.png", bbox_inches='tight')
    plt.close()
    return pr_auc

def evaluate_with_labels(anomaly_scores, y_true, model_name):
    """Compute supervised metrics using hidden labels"""
    from sklearn.metrics import f1_score, classification_report, confusion_matrix
    
    # Threshold at expected contamination rate
    threshold = np.percentile(anomaly_scores, (1 - CONTAMINATION) * 100)
    y_pred = (anomaly_scores >= threshold).astype(int)
    
    # Metrics
    f1 = f1_score(y_true, y_pred)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    # Recall @ 90% Precision
    from sklearn.metrics import precision_recall_curve
    precisions, recalls, thresholds = precision_recall_curve(y_true, anomaly_scores)
    target_idx = np.where(precisions[:-1] >= 0.9)[0]
    recall_at_90_prec = recalls[target_idx[-1]] if len(target_idx) > 0 else 0.0
    
    print(f"\n--- SUPERVISED METRICS (validation only) ---")
    print(f"F1-Score (@{CONTAMINATION:.1%} threshold): {f1:.4f}")
    print(f"Precision: {precision:.4f}, Recall: {recall:.4f}")
    print(f"Recall @ 90% Precision: {recall_at_90_prec:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"]))
    
    # Plot PR curve
    pr_auc = plot_precision_recall_curve(y_true, anomaly_scores, model_name)
    
    return {
        "f1_score": float(f1),
        "precision": float(precision),
        "recall": float(recall),
        "pr_auc": float(pr_auc),
        "recall_at_90_precision": float(recall_at_90_prec),
        "threshold_used": float(threshold),
        "confusion_matrix": [int(tn), int(fp), int(fn), int(tp)]
    }

def evaluate_model(model_name, prepare_func, is_customer=False):
    config = MODEL_CONFIG[model_name]
    print(f"\n{'='*60}")
    print(f"EVALUATING {model_name.upper()} MODEL")
    print(f"{'='*60}")
    
    # Load data
    df = pd.read_csv(config["data_path"])
    print(f"Loaded {len(df):,} records from {config['data_path']}")
    
    # Load model and scaler
    model = joblib.load(config["model_path"])
    scaler = joblib.load(config["scaler_path"])
    
    # ✅ FIX: Handle customer-level aggregation BEFORE feature preparation
    if is_customer:
        # Prepare customer-level features
        X, ids = prepare_func(df)
        
        # ✅ CRITICAL FIX: Aggregate labels at customer level
        if "is_anomaly" in df.columns:
            # Customer is anomalous if ANY of their transactions are anomalous
            customer_labels = df.groupby("customer_id")["is_anomaly"].max()
            # Align with customer IDs from feature extraction
            y_true = customer_labels.loc[ids].values
            has_labels = True
            print(f"⚠️  Aggregated {len(df)} transaction labels to {len(y_true)} customer labels")
            print(f"    Anomalous customers: {y_true.sum()} ({y_true.sum()/len(y_true)*100:.1f}%)")
        else:
            y_true = None
            has_labels = False
            print("ℹ️  No labels found — unsupervised evaluation only")
    else:
        # Non-customer models: standard flow
        X = prepare_func(df)
        ids = df[config["id_col"]] if config["id_col"] else df.index
        has_labels = "is_anomaly" in df.columns
        if has_labels:
            y_true = df["is_anomaly"].values
            print(f"⚠️  Found 'is_anomaly' column — computing supervised metrics")
        else:
            y_true = None
            print("ℹ️  No labels found — unsupervised evaluation only")
    
    # Predict
    X_scaled = scaler.transform(X)
    scores = model.score_samples(X_scaled)
    anomaly_scores = -scores  # Higher = more anomalous
    
    # Basic stats
    total = len(anomaly_scores)
    results = {
        "model_name": model_name,
        "total_samples": total,
        "anomaly_score_stats": {
            "mean": float(anomaly_scores.mean()),
            "std": float(anomaly_scores.std()),
            "min": float(anomaly_scores.min()),
            "max": float(anomaly_scores.max()),
            "median": float(np.median(anomaly_scores))
        },
        "has_labels": has_labels,
        "evaluation_timestamp": datetime.now().isoformat()
    }
    
    print(f"\n--- Basic Statistics ---")
    print(f"Total Samples: {total:,}")
    stats = results["anomaly_score_stats"]
    print(f"Anomaly Score - Mean: {stats['mean']:.4f}, Std: {stats['std']:.4f}")
    print(f"Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
    
    # Top anomalies
    top_n = min(100, total)
    top_idx = np.argsort(anomaly_scores)[-top_n:][::-1]
    top_df = pd.DataFrame({
        'id': [ids[i] for i in top_idx],
        'anomaly_score': anomaly_scores[top_idx]
    })
    top_path = OUTPUT_DIR / f"{model_name}_top_anomalies.csv"
    top_df.to_csv(top_path, index=False)
    results["top_anomalies_file"] = str(top_path)
    print(f"Top {top_n} anomalies saved to: {top_path}")
    
    # Score distribution plot
    plt.figure(figsize=(10, 6))
    sns.histplot(anomaly_scores, bins=50, kde=True)
    plt.title(f"{model_name.title()} Anomaly Score Distribution")
    plt.xlabel("Anomaly Score (higher = more anomalous)")
    plt.ylabel("Frequency")
    dist_path = OUTPUT_DIR / f"{model_name}_score_distribution.png"
    plt.savefig(dist_path, bbox_inches='tight')
    plt.close()
    results["score_distribution_plot"] = str(dist_path)
    
    # Supervised metrics (if labels exist)
    if has_labels:
        label_metrics = evaluate_with_labels(anomaly_scores, y_true, model_name)
        results["supervised_metrics"] = label_metrics
    
    # Save full results
    json_path = OUTPUT_DIR / f"{model_name}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    results["results_file"] = str(json_path)
    print(f"Evaluation results saved to: {json_path}")
    
    return results

def main():
    print("Evaluating all Isolation Forest models...")
    print("\nℹ️  Note: Only evaluating models that were actually trained:")
    print("   - Transaction model")
    print("   - Merged model (KYC + Business)")
    print("   - Customer model")
    print("   Skipping standalone KYC and Business models (not trained separately)\n")
    
    all_results = {}
    
    # Skip standalone KYC and Business models - they weren't trained
    # The training script only trains: merged, transaction, and customer models
    
    try:
        all_results["transaction"] = evaluate_model("transaction", prepare_transaction_features)
    except Exception as e:
        print(f"❌ Transaction model failed: {e}")
    
    try:
        all_results["merged"] = evaluate_model("merged", prepare_merged_features)
    except Exception as e:
        print(f"❌ Merged model failed: {e}")
    
    try:
        all_results["customer"] = evaluate_model("customer", prepare_customer_features, is_customer=True)
    except Exception as e:
        print(f"❌ Customer model failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final summary
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE!")
    print(f"{'='*60}")
    for name, res in all_results.items():
        if res:
            print(f"\n{name.upper()}:")
            print(f"  Samples: {res['total_samples']:,}")
            stats = res['anomaly_score_stats']
            print(f"  Score range: [{stats['min']:.3f}, {stats['max']:.3f}]")
            if res.get("supervised_metrics"):
                sm = res["supervised_metrics"]
                print(f"  F1-Score: {sm['f1_score']:.3f}")
                print(f"  PR-AUC: {sm['pr_auc']:.3f}")
                print(f"  Recall @ 90% Precision: {sm['recall_at_90_precision']:.3f}")

if __name__ == "__main__":
    main()
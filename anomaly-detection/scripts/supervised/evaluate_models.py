import json
import numpy as np
import pandas as pd
import joblib
import gc
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, average_precision_score, f1_score
)

# CRITICAL: Use separate test data that models haven't seen
MODEL_CONFIG = {
    "transaction": {
        "model_path": "data/models/transaction_rf_model.pkl",
        "scaler_path": "data/models/transaction_rf_scaler.pkl",
        "data_path": "data/eval/transaction_training_data.csv",
        "id_col": "customer_id",
        "test_size": 0.2  # Hold out 20% for testing
    },
    "merged": {
        "model_path": "data/models/merged_rf_model.pkl",
        "scaler_path": "data/models/merged_rf_scaler.pkl",
        "data_path": "data/eval/kyc_business_training_data.csv",
        "id_col": "customerId",
        "test_size": 0.2
    },
    "customer": {
        "model_path": "data/models/customer_rf_model.pkl",
        "scaler_path": "data/models/customer_rf_scaler.pkl",
        "data_path": "data/eval/transaction_training_data.csv",
        "id_col": None,
        "test_size": 0.2
    }
}

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================
# FEATURE PREPARATION (same as before)
# ==========================================

def prepare_kyc_features(df: pd.DataFrame) -> np.ndarray:
    """Extract KYC features efficiently"""
    features = []
    features.append(df["customer_age"])
    
    gender = df["customer_gender"].astype(str).str.lower().str.contains("female").astype(int)
    features.append(gender)
    
    marital = df["customer_marital_status"].astype(str).str.lower()
    marital_map = {"single": 0, "unmarried": 0, "married": 1, "divorced": 2, "widowed": 3}
    features.append(marital.map(marital_map).fillna(-1))
    
    education = df["customer_education_level"].astype(str).str.lower()
    edu_map = {
        "no_education_background": 0, "no_educational_background": 0,
        "primary": 1, "secondary": 2, "certificate": 3, "diploma": 4,
        "bachelors_degree": 5, "bachelor": 5, "masters_degree": 6,
        "master": 6, "phd_and_above": 7, "phd": 7
    }
    features.append(education.map(edu_map).fillna(-1))
    
    features.append(pd.Categorical(df["customer_region"]).codes)
    features.append(pd.Categorical(df["customer_city"]).codes)
    features.append(pd.Categorical(df["customer_zone_or_sub_city"]).codes)
    features.append(pd.to_numeric(df["customer_woreda"], errors="coerce").fillna(0))
    
    phone_str = df["customer_phone_number"].astype(str)
    features.append(phone_str.str[-4:].astype(int))
    features.append(phone_str.apply(lambda x: len(set(x)) / len(x) if len(x) > 0 else 0))
    
    features.append(df["customer_tin_number"].astype(str).str.len())
    features.append(df["customer_bank_account_number"].astype(str).str.len())
    
    edu_encoded = features[3]
    features.append(np.where(edu_encoded > 0, df["customer_age"] / (edu_encoded + 1), 0))
    
    return np.column_stack(features)


def prepare_business_features(df: pd.DataFrame) -> np.ndarray:
    """Extract business features with safe handling"""
    features = []
    
    features.append(2024 - df["business_establishment_year"])
    
    sector_map = {"agriculture": 0, "manufacturing": 1, "domestic_trade_services": 2, "services": 3, "other": 4}
    features.append(df["business_sector"].astype(str).str.lower().map(sector_map).fillna(-1))
    
    level_map = {"growing": 0, "startup": 1}
    features.append(df["business_level"].astype(str).str.lower().map(level_map).fillna(-1))
    
    # Safe capital handling
    starting_cap = df["business_starting_capital"].clip(lower=0)
    current_cap = df["business_current_capital"].clip(lower=0)
    features.extend([starting_cap, current_cap, np.log1p(starting_cap), np.log1p(current_cap)])
    
    # Safe financial handling
    annual_profit = df["business_annual_profit"]
    annual_sales = df["business_annual_sales"].clip(lower=0)
    features.extend([
        annual_profit, 
        annual_sales, 
        np.log1p(np.abs(annual_profit)),  # Use abs for negative profits
        np.log1p(annual_sales)
    ])
    
    start_emp = df["business_starting_no_of_employees"].clip(lower=0)
    current_emp = df["business_current_no_of_employees"].clip(lower=0)
    features.extend([start_emp, current_emp])
    
    source_map = {"family": 0, "own": 1, "loan": 2, "fund": 3, "other": 4}
    features.append(df["business_source_of_initial_capital"].astype(str).str.lower().map(source_map).fillna(-1))
    
    assoc_map = {"sole_proprietorship": 0, "partnership": 1, "corporation": 2, "other": 3}
    features.append(df["business_association_type"].astype(str).str.lower().map(assoc_map).fillna(-1))
    
    # Safe ratios
    features.append(np.where(starting_cap > 0, np.clip(current_cap / starting_cap, 0, 10), 0))
    features.append(np.where(start_emp > 0, np.clip(current_emp / start_emp, 0, 10), 0))
    features.append(np.where(annual_sales > 0, np.clip(annual_profit / annual_sales, -1, 1), 0))
    features.append(np.where(current_cap > 0, np.clip(annual_profit / current_cap, -1, 1), 0))
    features.append(np.log1p(np.where(current_emp > 0, annual_sales / current_emp, 0)))
    features.append(np.where(current_cap > 0, annual_sales / current_cap, 0))
    
    cap_growth = features[-6]
    emp_growth = features[-5]
    features.append(np.abs(cap_growth - emp_growth))
    
    business_age = features[0]
    features.append(np.where(business_age > 0, np.log1p(current_cap) / np.log1p(business_age + 1), 0))
    
    return np.column_stack(features)


def prepare_customer_features(df: pd.DataFrame, chunk_size: int = 1000) -> tuple[np.ndarray, list]:
    """Extract customer features with chunking"""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    
    customer_ids = []
    customer_features = []
    customers = df["customer_id"].unique()
    
    print(f"Processing {len(customers)} customers in chunks of {chunk_size}")
    
    for i in range(0, len(customers), chunk_size):
        chunk_customers = customers[i:i+chunk_size]
        chunk_df = df[df["customer_id"].isin(chunk_customers)]
        
        for customer_id, group in chunk_df.groupby("customer_id"):
            customer_ids.append(customer_id)
            n_txns = len(group)
            features = []
            
            features.extend([n_txns, np.log1p(n_txns)])
            
            features.extend([
                group["credit"].sum(), group["debit"].sum(),
                group["credit"].mean(), group["debit"].mean(),
                group["credit"].max(), group["debit"].max(),
                group["credit"].std() if n_txns > 1 else 0.0,
                group["debit"].std() if n_txns > 1 else 0.0
            ])
            
            features.append(np.log1p(features[-8] / (features[-7] + 1)))
            
            features.extend([
                group["closingBalance"].mean(), group["closingBalance"].max(),
                group["closingBalance"].min(), group["closingBalance"].std() if n_txns > 1 else 0.0
            ])
            
            txn_amt = group["credit"] - group["debit"]
            features.extend([
                txn_amt.mean(), txn_amt.max(), txn_amt.min(),
                txn_amt.std() if n_txns > 1 else 0.0, txn_amt.median()
            ])
            
            total = max(n_txns, 1)
            source_counts = group["source"].value_counts()
            features.extend([
                len(source_counts),
                source_counts.iloc[0] / total if len(source_counts) > 0 else 0.0,
                group["source"].str.contains("CASH DEPOSIT", case=False, na=False).sum() / total,
                group["source"].str.contains("FUND TRANSFER", case=False, na=False).sum() / total,
                group["source"].str.contains("CASH WITHDRAW", case=False, na=False).sum() / total,
                group["source"].str.contains("TELE BIRR", case=False, na=False).sum() / total
            ])
            
            hours = group["date"].dt.hour
            features.extend([
                hours.mean(), hours.std() if n_txns > 1 else 0.0,
                ((hours >= 22) | (hours <= 6)).sum() / total,
                ((hours >= 9) & (hours <= 17)).sum() / total
            ])
            
            dow = group["date"].dt.dayofweek
            features.extend([
                (dow < 5).sum() / total,
                (dow >= 5).sum() / total
            ])
            
            if n_txns > 1:
                diffs = group["date"].sort_values().diff().dt.total_seconds().fillna(0) / 3600
                features.extend([diffs.mean(), diffs.median(), diffs.min(), diffs.max(), diffs.std()])
                features.append((diffs < 1).sum() / max(n_txns - 1, 1))
            else:
                features.extend([0.0] * 6)
            
            narr = group["narrative"].fillna("")
            features.extend([
                narr.str.len().mean(), narr.nunique(),
                narr.nunique() / total, (narr.str.len() < 5).sum() / total
            ])
            
            balance = group["closingBalance"]
            bal_ratio = np.where(balance > 0, txn_amt / balance, 0)
            features.extend([
                np.mean(bal_ratio), np.max(bal_ratio),
                np.std(bal_ratio) if n_txns > 1 else 0.0
            ])
            
            high_thresh = txn_amt.quantile(0.9) if n_txns > 0 else 0
            features.append((np.abs(txn_amt) > high_thresh).sum() / total)
            features.append(((group["credit"] % 1000 == 0) | (group["debit"] % 1000 == 0)).sum() / total)
            
            lifetime = (group["date"].max() - group["date"].min()).days
            features.extend([lifetime, n_txns / max(lifetime, 1)])
            
            customer_features.append([float(x) if pd.notna(x) else 0.0 for x in features])
        
        del chunk_df
        gc.collect()
        
        if (i // chunk_size + 1) % 5 == 0:
            print(f"  Processed {min(i+chunk_size, len(customers))} / {len(customers)} customers")
    
    return np.array(customer_features, dtype=np.float32), customer_ids


def prepare_transaction_features(df: pd.DataFrame) -> np.ndarray:
    """Extract transaction features"""
    df = df.copy()
    features = []
    
    credit, debit, balance = df["credit"], df["debit"], df["closingBalance"]
    features.extend([credit, debit, balance, np.log1p(credit), np.log1p(debit), np.log1p(balance)])
    
    source_map = {"cash deposit": 0, "fund transfer": 1, "cash withdraw": 2,
                  "tele birr incoming": 3, "tele birr out going": 4, "atm card subscription fee": 5}
    features.append(df["source"].str.lower().map(source_map).fillna(-1))
    
    src = df["source"].str.lower().fillna("")
    features.extend([
        src.str.contains("cash deposit").astype(int),
        src.str.contains("fund transfer").astype(int),
        src.str.contains("cash withdraw").astype(int),
        src.str.contains("tele birr").astype(int)
    ])
    
    narr = df["narrative"].fillna("")
    features.extend([narr.str.len(), (narr.str.len() < 5).astype(int)])
    
    txn_amt = credit - debit
    features.extend([txn_amt, np.abs(txn_amt)])
    features.extend([
        np.clip(np.where(balance > 0, txn_amt / balance, 0), -10, 10),
        np.clip(np.where(balance > 0, np.abs(txn_amt) / balance, 0), 0, 10)
    ])
    
    features.extend([
        (credit % 1000 == 0).astype(int),
        (debit % 1000 == 0).astype(int),
        ((credit % 1000 == 0) | (debit % 1000 == 0)).astype(int)
    ])
    
    df["date"] = pd.to_datetime(df["date"])
    hour, dow, day, month = df["date"].dt.hour, df["date"].dt.dayofweek, df["date"].dt.day, df["date"].dt.month
    features.extend([hour, dow, day, month])
    features.extend([
        ((hour >= 9) & (hour <= 17)).astype(int),
        ((hour >= 22) | (hour <= 6)).astype(int),
        (dow >= 5).astype(int),
        (dow < 5).astype(int)
    ])
    
    cust_txn_cnt = df.groupby("customer_id").size()
    cust_credit_sum = df.groupby("customer_id")["credit"].sum()
    cust_debit_sum = df.groupby("customer_id")["debit"].sum()
    cust_credit_avg = df.groupby("customer_id")["credit"].mean()
    cust_debit_avg = df.groupby("customer_id")["debit"].mean()
    cust_credit_max = df.groupby("customer_id")["credit"].max()
    cust_debit_max = df.groupby("customer_id")["debit"].max()
    cust_balance_avg = df.groupby("customer_id")["closingBalance"].mean()
    
    txn_freq = df["customer_id"].map(cust_txn_cnt)
    features.extend([txn_freq, np.log1p(txn_freq)])
    
    c_credit_tot = df["customer_id"].map(cust_credit_sum)
    c_debit_tot = df["customer_id"].map(cust_debit_sum)
    features.extend([c_credit_tot, c_debit_tot, np.log1p(c_credit_tot / (c_debit_tot + 1))])
    
    features.extend([
        np.where(c_credit_tot > 0, credit / c_credit_tot, 0),
        np.where(c_debit_tot > 0, debit / c_debit_tot, 0)
    ])
    
    daily_cnt = df.groupby(["customer_id", df["date"].dt.date]).size()
    df["daily_vel"] = df.set_index(["customer_id", df["date"].dt.date]).index.map(daily_cnt).fillna(1)
    features.extend([df["daily_vel"], (df["daily_vel"] > 5).astype(int)])
    
    c_avg_credit = df["customer_id"].map(cust_credit_avg)
    c_avg_debit = df["customer_id"].map(cust_debit_avg)
    features.extend([c_avg_credit, c_avg_debit])
    
    features.extend([
        np.where(c_avg_credit > 0, (credit - c_avg_credit) / c_avg_credit, 0),
        np.where(c_avg_debit > 0, (debit - c_avg_debit) / c_avg_debit, 0)
    ])
    
    c_max_credit = df["customer_id"].map(cust_credit_max)
    c_max_debit = df["customer_id"].map(cust_debit_max)
    features.extend([
        (credit == c_max_credit).astype(int),
        (debit == c_max_debit).astype(int)
    ])
    
    features.extend([
        (credit > np.where(c_avg_credit > 0, c_avg_credit * 2, 10000)).astype(int),
        (debit > np.where(c_avg_debit > 0, c_avg_debit * 2, 10000)).astype(int)
    ])
    
    c_avg_bal = df["customer_id"].map(cust_balance_avg)
    features.extend([
        c_avg_bal,
        np.where(c_avg_bal > 0, (balance - c_avg_bal) / c_avg_bal, 0)
    ])
    
    return np.column_stack(features)


def prepare_merged_features(df: pd.DataFrame) -> np.ndarray:
    """Prepare combined KYC + Business features"""
    kyc_features = prepare_kyc_features(df)
    business_features = prepare_business_features(df)
    return np.column_stack([kyc_features, business_features])


# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================

def plot_confusion_matrix(y_true, y_pred, model_name):
    """Plot confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Normal', 'Anomaly'],
                yticklabels=['Normal', 'Anomaly'])
    plt.title(f'{model_name.title()} Confusion Matrix (Test Set)')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(OUTPUT_DIR / f"{model_name}_confusion_matrix_test.png", bbox_inches='tight')
    plt.close()


def plot_precision_recall_curve(y_true, y_proba, model_name):
    """Plot precision-recall curve"""
    precision, recall, _ = precision_recall_curve(y_true, y_proba)
    pr_auc = average_precision_score(y_true, y_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, marker='.', label=f'PR AUC = {pr_auc:.3f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'{model_name.title()} Precision-Recall Curve (Test Set)')
    plt.legend()
    plt.grid(True)
    plt.savefig(OUTPUT_DIR / f"{model_name}_precision_recall_curve_test.png", bbox_inches='tight')
    plt.close()
    return pr_auc


def plot_probability_distribution(y_true, y_proba, model_name):
    """Plot prediction probability distribution"""
    plt.figure(figsize=(10, 6))
    plt.hist(y_proba[y_true == 0], bins=50, alpha=0.5, label='Normal', density=True)
    plt.hist(y_proba[y_true == 1], bins=50, alpha=0.5, label='Anomaly', density=True)
    plt.xlabel('Predicted Probability of Anomaly')
    plt.ylabel('Density')
    plt.title(f'{model_name.title()} Probability Distribution (Test Set)')
    plt.legend()
    plt.savefig(OUTPUT_DIR / f"{model_name}_probability_distribution_test.png", bbox_inches='tight')
    plt.close()


# ==========================================
# EVALUATION WITH PROPER SPLIT
# ==========================================

def evaluate_model_with_split(model_name, prepare_func, is_customer=False, chunk_size=1000):
    """
    Evaluate model with proper train/test split
    CRITICAL: Test on data the model has never seen
    """
    config = MODEL_CONFIG[model_name]
    print(f"\n{'='*60}")
    print(f"EVALUATING {model_name.upper()} MODEL (WITH PROPER SPLIT)")
    print(f"{'='*60}")
    
    # Load full dataset
    df = pd.read_csv(config["data_path"])
    print(f"Loaded {len(df):,} records from {config['data_path']}")
    
    if "label" not in df.columns:
        print(f"❌ No 'label' column found - cannot evaluate")
        return None
    
    # Load trained model and scaler
    try:
        model = joblib.load(config["model_path"])
        scaler = joblib.load(config["scaler_path"])
        print(f"✓ Loaded model and scaler")
    except FileNotFoundError as e:
        print(f"❌ Model files not found: {e}")
        return None
    
    # Create train/test split
    test_size = config["test_size"]
    
    if is_customer:
        # For customer model: split by customer_id to avoid leakage
        customer_ids = df["customer_id"].unique()
        train_customers, test_customers = train_test_split(
            customer_ids, test_size=test_size, random_state=42, 
            stratify=None  # Can't stratify on customer IDs directly
        )
        
        train_df = df[df["customer_id"].isin(train_customers)]
        test_df = df[df["customer_id"].isin(test_customers)]
        
        print(f"Split: {len(train_customers)} train customers, {len(test_customers)} test customers")
        print(f"  Train transactions: {len(train_df):,}")
        print(f"  Test transactions: {len(test_df):,}")
        
        # Prepare customer-level features for test set
        X_test, test_ids = prepare_func(test_df, chunk_size=chunk_size)
        
        # Aggregate labels at customer level
        customer_labels = test_df.groupby("customer_id")["label"].max()
        y_test = customer_labels.loc[test_ids].values.astype(int)
        
        print(f"✓ Test set: {len(y_test)} customers, {y_test.sum()} anomalies ({y_test.sum()/len(y_test)*100:.1f}%)")
        
    else:
        # For transaction/merged models: standard split
        if model_name == "transaction":
            # For transaction model, split by customer_id to avoid data leakage
            customer_ids = df["customer_id"].unique()
            train_customers, test_customers = train_test_split(
                customer_ids, test_size=test_size, random_state=42
            )
            train_df = df[df["customer_id"].isin(train_customers)]
            test_df = df[df["customer_id"].isin(test_customers)]
            print(f"Split by customer: {len(train_customers)} train, {len(test_customers)} test")
        else:
            # For merged model: standard row-level split
            train_df, test_df = train_test_split(
                df, test_size=test_size, random_state=42,
                stratify=df["label"]
            )
            print(f"Split: {len(train_df)} train, {len(test_df)} test rows")
        
        X_test = prepare_func(test_df)
        y_test = test_df["label"].values.astype(int)
        test_ids = test_df[config["id_col"]] if config["id_col"] else test_df.index
        
        print(f"✓ Test set: {len(y_test):,} samples, {y_test.sum()} anomalies ({y_test.sum()/len(y_test)*100:.1f}%)")
    
    # Generate predictions on TEST SET
    print(f"\nGenerating predictions on held-out test set...")
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # Calculate metrics
    total = len(y_pred)
    n_anomalies = y_pred.sum()
    
    results = {
        "model_name": model_name,
        "test_samples": int(total),
        "predicted_anomalies": int(n_anomalies),
        "predicted_anomaly_rate": float(n_anomalies / total),
        "true_anomaly_rate": float(y_test.sum() / total),
        "evaluation_timestamp": datetime.now().isoformat()
    }
    
    print(f"\n--- Test Set Statistics ---")
    print(f"Total Samples: {total:,}")
    print(f"True Anomalies: {y_test.sum():,} ({y_test.sum()/total*100:.2f}%)")
    print(f"Predicted Anomalies: {n_anomalies:,} ({n_anomalies/total*100:.2f}%)")
    
    # Supervised metrics
    try:
        auc = roc_auc_score(y_test, y_proba)
        pr_auc = plot_precision_recall_curve(y_test, y_proba, model_name)
        f1 = f1_score(y_test, y_pred)
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # Recall @ 90% Precision
        precisions, recalls, _ = precision_recall_curve(y_test, y_proba)
        target_idx = np.where(precisions[:-1] >= 0.9)[0]
        recall_at_90_prec = recalls[target_idx[-1]] if len(target_idx) > 0 else 0.0
        
        results["metrics"] = {
            "roc_auc": float(auc),
            "pr_auc": float(pr_auc),
            "f1_score": float(f1),
            "precision": float(precision),
            "recall": float(recall),
            "recall_at_90_precision": float(recall_at_90_prec),
            "confusion_matrix": {
                "tn": int(tn), "fp": int(fp),
                "fn": int(fn), "tp": int(tp)
            }
        }
        
        print(f"\n--- SUPERVISED METRICS (Test Set) ---")
        print(f"ROC AUC: {auc:.4f}")
        print(f"PR AUC: {pr_auc:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print(f"Precision: {precision:.4f}, Recall: {recall:.4f}")
        print(f"Recall @ 90% Precision: {recall_at_90_prec:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=["Normal", "Anomaly"]))
        
        # Generate plots
        plot_confusion_matrix(y_test, y_pred, model_name)
        plot_probability_distribution(y_test, y_proba, model_name)
        
    except Exception as e:
        print(f"⚠️  Error calculating metrics: {e}")
        import traceback
        traceback.print_exc()
    
    # Save predictions
    pred_df = pd.DataFrame({
        'id': test_ids,
        'predicted_label': y_pred,
        'anomaly_probability': y_proba,
        'true_label': y_test
    })
    
    pred_path = OUTPUT_DIR / f"{model_name}_test_predictions.csv"
    pred_df.to_csv(pred_path, index=False)
    results["predictions_file"] = str(pred_path)
    print(f"✓ Test predictions saved to: {pred_path}")
    
    # Top anomalies from test set
    top_n = min(100, total)
    top_idx = np.argsort(y_proba)[-top_n:][::-1]
    top_df = pred_df.iloc[top_idx]
    top_path = OUTPUT_DIR / f"{model_name}_top_anomalies_test.csv"
    top_df.to_csv(top_path, index=False)
    results["top_anomalies_file"] = str(top_path)
    print(f"✓ Top {top_n} anomalies saved to: {top_path}")
    
    # Save results
    json_path = OUTPUT_DIR / f"{model_name}_test_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    results["results_file"] = str(json_path)
    print(f"✓ Results saved to: {json_path}")
    
    # Cleanup
    del test_df, X_test, X_test_scaled, y_pred, y_proba, y_test
    gc.collect()
    
    return results


def main():
    """Run proper evaluation with train/test split"""
    print("=" * 70)
    print("PROPER MODEL EVALUATION (WITH HELD-OUT TEST SET)")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: Evaluating on held-out test data (20%)")
    print("   Models trained on 80%, tested on unseen 20%")
    print("   This prevents overfitting and gives realistic performance\n")
    
    all_results = {}
    
    # 1. Transaction Model
    print("\n" + "=" * 70)
    try:
        all_results["transaction"] = evaluate_model_with_split(
            "transaction",
            prepare_transaction_features,
            is_customer=False
        )
    except Exception as e:
        print(f"❌ Transaction model evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. Merged Model
    print("\n" + "=" * 70)
    try:
        all_results["merged"] = evaluate_model_with_split(
            "merged",
            prepare_merged_features,
            is_customer=False
        )
    except Exception as e:
        print(f"❌ Merged model evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Customer Model
    print("\n" + "=" * 70)
    try:
        all_results["customer"] = evaluate_model_with_split(
            "customer",
            prepare_customer_features,
            is_customer=True,
            chunk_size=1000
        )
    except Exception as e:
        print(f"❌ Customer model evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final Summary
    print(f"\n{'='*70}")
    print("TEST SET EVALUATION SUMMARY")
    print(f"{'='*70}")
    print("\n🎯 These are REALISTIC performance metrics (on unseen data):\n")
    
    for name, res in all_results.items():
        if res:
            print(f"{name.upper()}:")
            print(f"  Test Samples: {res['test_samples']:,}")
            print(f"  True Anomaly Rate: {res['true_anomaly_rate']*100:.2f}%")
            print(f"  Predicted Anomaly Rate: {res['predicted_anomaly_rate']*100:.2f}%")
            
            if res.get("metrics"):
                m = res["metrics"]
                print(f"  ROC AUC: {m['roc_auc']:.4f}")
                print(f"  PR AUC: {m['pr_auc']:.4f}")
                print(f"  F1-Score: {m['f1_score']:.4f}")
                print(f"  Precision: {m['precision']:.4f}")
                print(f"  Recall: {m['recall']:.4f}")
                print(f"  Recall @ 90% Precision: {m['recall_at_90_precision']:.4f}")
                
                cm = m["confusion_matrix"]
                print(f"  Confusion Matrix: TN={cm['tn']}, FP={cm['fp']}, FN={cm['fn']}, TP={cm['tp']}")
            print()
    
    print(f"{'='*70}")
    print(f"✅ PROPER EVALUATION COMPLETE!")
    print(f"   Test set results saved to: {OUTPUT_DIR}/")
    print(f"{'='*70}")
    
    # Warning if perfect scores
    for name, res in all_results.items():
        if res and res.get("metrics"):
            if res["metrics"]["roc_auc"] >= 0.999:
                print(f"\n⚠️  WARNING: {name.upper()} model has near-perfect AUC ({res['metrics']['roc_auc']:.4f})")
                print(f"   This may indicate:")
                print(f"   1. Data leakage between train/test sets")
                print(f"   2. Synthetic/unrealistic data labels")
                print(f"   3. Very simple anomaly patterns")
                print(f"   Consider investigating further!")


if __name__ == "__main__":
    main()
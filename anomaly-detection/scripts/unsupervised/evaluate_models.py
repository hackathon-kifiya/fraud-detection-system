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
CONTAMINATION = 0.01


def prepare_kyc_features(df: pd.DataFrame) -> np.ndarray:
    """Extract KYC features efficiently"""
    features = []

    # Demographics
    features.append(df["customer_age"])

    # Gender (0=male, 1=female)
    gender = df["customer_gender"].astype(str).str.lower().str.contains("female").astype(int)
    features.append(gender)

    # Marital status
    marital = df["customer_marital_status"].astype(str).str.lower()
    marital_map = {"single": 0, "unmarried": 0, "married": 1, "divorced": 2, "widowed": 3}
    features.append(marital.map(marital_map).fillna(-1))

    # Education level
    education = df["customer_education_level"].astype(str).str.lower()
    edu_map = {
        "no_education_background": 0, "no_educational_background": 0,
        "primary": 1, "secondary": 2, "certificate": 3, "diploma": 4,
        "bachelors_degree": 5, "bachelor": 5, "masters_degree": 6,
        "master": 6, "phd_and_above": 7, "phd": 7
    }
    features.append(education.map(edu_map).fillna(-1))

    # Location (categorical codes)
    features.append(pd.Categorical(df["customer_region"]).codes)
    features.append(pd.Categorical(df["customer_city"]).codes)
    features.append(pd.Categorical(df["customer_zone_or_sub_city"]).codes)
    features.append(pd.to_numeric(df["customer_woreda"], errors="coerce").fillna(0))

    # Phone patterns
    phone_str = df["customer_phone_number"].astype(str)
    features.append(phone_str.str[-4:].astype(int))
    features.append(phone_str.apply(lambda x: len(set(x)) / len(x) if len(x) > 0 else 0))

    # ID lengths
    features.append(df["customer_tin_number"].astype(str).str.len())
    features.append(df["customer_bank_account_number"].astype(str).str.len())

    # Age-education ratio
    edu_encoded = features[3]
    features.append(np.where(edu_encoded > 0, df["customer_age"] / (edu_encoded + 1), 0))

    return np.column_stack(features)


def prepare_business_features(df: pd.DataFrame) -> np.ndarray:
    """Extract business features efficiently"""
    features = []

    # Business age
    features.append(2024 - df["business_establishment_year"])

    # Sector
    sector_map = {"agriculture": 0, "manufacturing": 1, "domestic_trade_services": 2, "services": 3, "other": 4}
    features.append(df["business_sector"].astype(str).str.lower().map(sector_map).fillna(-1))

    # Level
    level_map = {"growing": 0, "startup": 1}
    features.append(df["business_level"].astype(str).str.lower().map(level_map).fillna(-1))

    # Capital
    starting_cap = df["business_starting_capital"]
    current_cap = df["business_current_capital"]
    features.extend([starting_cap, current_cap, np.log1p(starting_cap), np.log1p(current_cap)])

    # Financials
    annual_profit = df["business_annual_profit"]
    annual_sales = df["business_annual_sales"]
    features.extend([annual_profit, annual_sales, np.log1p(np.abs(annual_profit)), np.log1p(annual_sales)])

    # Employees
    start_emp = df["business_starting_no_of_employees"]
    current_emp = df["business_current_no_of_employees"]
    features.extend([start_emp, current_emp])

    # Source & Association
    source_map = {"family": 0, "own": 1, "loan": 2, "fund": 3, "other": 4}
    features.append(df["business_source_of_initial_capital"].astype(str).str.lower().map(source_map).fillna(-1))

    assoc_map = {"sole_proprietorship": 0, "partnership": 1, "corporation": 2, "other": 3}
    features.append(df["business_association_type"].astype(str).str.lower().map(assoc_map).fillna(-1))

    # Derived ratios
    features.append(np.where(starting_cap > 0, np.clip(current_cap / starting_cap, 0, 10), 0))
    features.append(np.where(start_emp > 0, np.clip(current_emp / start_emp, 0, 10), 0))
    features.append(np.where(annual_sales > 0, np.clip(annual_profit / annual_sales, -1, 1), 0))
    features.append(np.where(current_cap > 0, np.clip(annual_profit / current_cap, -1, 1), 0))
    features.append(np.log1p(np.where(current_emp > 0, annual_sales / current_emp, 0)))
    features.append(np.where(current_cap > 0, annual_sales / current_cap, 0))

    # Consistency checks
    cap_growth = features[-6]
    emp_growth = features[-5]
    features.append(np.abs(cap_growth - emp_growth))

    business_age = features[0]
    features.append(np.where(business_age > 0, np.log1p(current_cap) / np.log1p(business_age + 1), 0))

    return np.column_stack(features)


def prepare_customer_features(df: pd.DataFrame, chunk_size: int = 1000) -> tuple[np.ndarray, list]:
    """
    Extract customer features with memory optimization
    Process customers in chunks to reduce memory usage
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    customer_ids = []
    customer_features = []

    # Process in chunks
    customers = df["customer_id"].unique()
    print(f"Processing {len(customers)} customers in chunks of {chunk_size}")

    for i in range(0, len(customers), chunk_size):
        chunk_customers = customers[i:i+chunk_size]
        chunk_df = df[df["customer_id"].isin(chunk_customers)]

        for customer_id, group in chunk_df.groupby("customer_id"):
            customer_ids.append(customer_id)
            n_txns = len(group)
            features = []

            # Transaction volume
            features.extend([n_txns, np.log1p(n_txns)])

            # Credit/Debit stats
            features.extend([
                group["credit"].sum(), group["debit"].sum(),
                group["credit"].mean(), group["debit"].mean(),
                group["credit"].max(), group["debit"].max(),
                group["credit"].std() if n_txns > 1 else 0.0,
                group["debit"].std() if n_txns > 1 else 0.0
            ])

            # CD ratio
            features.append(np.log1p(features[-8] / (features[-7] + 1)))

            # Balance stats
            features.extend([
                group["closingBalance"].mean(), group["closingBalance"].max(),
                group["closingBalance"].min(), group["closingBalance"].std() if n_txns > 1 else 0.0
            ])

            # Transaction amounts
            txn_amt = group["credit"] - group["debit"]
            features.extend([
                txn_amt.mean(), txn_amt.max(), txn_amt.min(),
                txn_amt.std() if n_txns > 1 else 0.0, txn_amt.median()
            ])

            # Source diversity
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

            # Temporal patterns
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

            # Velocity
            if n_txns > 1:
                diffs = group["date"].sort_values().diff().dt.total_seconds().fillna(0) / 3600
                features.extend([diffs.mean(), diffs.median(), diffs.min(), diffs.max(), diffs.std()])
                features.append((diffs < 1).sum() / max(n_txns - 1, 1))
            else:
                features.extend([0.0] * 6)

            # Narrative patterns
            narr = group["narrative"].fillna("")
            features.extend([
                narr.str.len().mean(), narr.nunique(),
                narr.nunique() / total, (narr.str.len() < 5).sum() / total
            ])

            # Balance behavior
            balance = group["closingBalance"]
            bal_ratio = np.where(balance > 0, txn_amt / balance, 0)
            features.extend([
                np.mean(bal_ratio), np.max(bal_ratio),
                np.std(bal_ratio) if n_txns > 1 else 0.0
            ])

            # Risk indicators
            high_thresh = txn_amt.quantile(0.9) if n_txns > 0 else 0
            features.append((np.abs(txn_amt) > high_thresh).sum() / total)
            features.append(((group["credit"] % 1000 == 0) | (group["debit"] % 1000 == 0)).sum() / total)

            # Activity metrics
            lifetime = (group["date"].max() - group["date"].min()).days
            features.extend([lifetime, n_txns / max(lifetime, 1)])

            customer_features.append([float(x) if pd.notna(x) else 0.0 for x in features])

        # Clean up memory after each chunk
        del chunk_df
        gc.collect()

        if (i // chunk_size + 1) % 5 == 0:
            print(f"  Processed {min(i+chunk_size, len(customers))} / {len(customers)} customers")

    X = np.array(customer_features, dtype=np.float32)
    print(f"Generated {X.shape[1]} features for {len(customer_ids)} customers")
    return X, customer_ids


def prepare_transaction_features(df: pd.DataFrame, sample_frac: float = 1.0) -> np.ndarray:
    """
    Extract transaction features with optional sampling for memory efficiency

    Args:
        df: Transaction dataframe
        sample_frac: Fraction of data to sample (1.0 = use all, 0.1 = use 10%)
    """
    if sample_frac < 1.0:
        df = df.sample(frac=sample_frac, random_state=42)
        print(f"Sampling {sample_frac*100:.0f}% of transactions: {len(df)} records")

    df = df.copy()
    features = []

    # Basic amounts
    credit, debit, balance = df["credit"], df["debit"], df["closingBalance"]
    features.extend([credit, debit, balance, np.log1p(credit), np.log1p(debit), np.log1p(balance)])

    # Source encoding
    source_map = {"cash deposit": 0, "fund transfer": 1, "cash withdraw": 2,
                  "tele birr incoming": 3, "tele birr out going": 4, "atm card subscription fee": 5}
    features.append(df["source"].str.lower().map(source_map).fillna(-1))

    # Source indicators
    src = df["source"].str.lower().fillna("")
    features.extend([
        src.str.contains("cash deposit").astype(int),
        src.str.contains("fund transfer").astype(int),
        src.str.contains("cash withdraw").astype(int),
        src.str.contains("tele birr").astype(int)
    ])

    # Narrative
    narr = df["narrative"].fillna("")
    features.extend([narr.str.len(), (narr.str.len() < 5).astype(int)])

    # Transaction amounts
    txn_amt = credit - debit
    features.extend([txn_amt, np.abs(txn_amt)])
    features.extend([
        np.clip(np.where(balance > 0, txn_amt / balance, 0), -10, 10),
        np.clip(np.where(balance > 0, np.abs(txn_amt) / balance, 0), 0, 10)
    ])

    # Round amounts
    features.extend([
        (credit % 1000 == 0).astype(int),
        (debit % 1000 == 0).astype(int),
        ((credit % 1000 == 0) | (debit % 1000 == 0)).astype(int)
    ])

    # Temporal
    df["date"] = pd.to_datetime(df["date"])
    hour, dow, day, month = df["date"].dt.hour, df["date"].dt.dayofweek, df["date"].dt.day, df["date"].dt.month
    features.extend([hour, dow, day, month])
    features.extend([
        ((hour >= 9) & (hour <= 17)).astype(int),
        ((hour >= 22) | (hour <= 6)).astype(int),
        (dow >= 5).astype(int),
        (dow < 5).astype(int)
    ])

    # Customer aggregations (compute once, reuse)
    cust_txn_cnt = df.groupby("customer_id").size()
    cust_credit_sum = df.groupby("customer_id")["credit"].sum()
    cust_debit_sum = df.groupby("customer_id")["debit"].sum()
    cust_credit_avg = df.groupby("customer_id")["credit"].mean()
    cust_debit_avg = df.groupby("customer_id")["debit"].mean()
    cust_credit_max = df.groupby("customer_id")["credit"].max()
    cust_debit_max = df.groupby("customer_id")["debit"].max()
    cust_balance_avg = df.groupby("customer_id")["closingBalance"].mean()

    # Map to transactions
    txn_freq = df["customer_id"].map(cust_txn_cnt)
    features.extend([txn_freq, np.log1p(txn_freq)])

    c_credit_tot = df["customer_id"].map(cust_credit_sum)
    c_debit_tot = df["customer_id"].map(cust_debit_sum)
    features.extend([c_credit_tot, c_debit_tot, np.log1p(c_credit_tot / (c_debit_tot + 1))])

    features.extend([
        np.where(c_credit_tot > 0, credit / c_credit_tot, 0),
        np.where(c_debit_tot > 0, debit / c_debit_tot, 0)
    ])

    # Daily velocity
    daily_cnt = df.groupby(["customer_id", df["date"].dt.date]).size()
    df["daily_vel"] = df.set_index(["customer_id", df["date"].dt.date]).index.map(daily_cnt).fillna(1)
    features.extend([df["daily_vel"], (df["daily_vel"] > 5).astype(int)])

    # Customer averages
    c_avg_credit = df["customer_id"].map(cust_credit_avg)
    c_avg_debit = df["customer_id"].map(cust_debit_avg)
    features.extend([c_avg_credit, c_avg_debit])

    # Deviations
    features.extend([
        np.where(c_avg_credit > 0, (credit - c_avg_credit) / c_avg_credit, 0),
        np.where(c_avg_debit > 0, (debit - c_avg_debit) / c_avg_debit, 0)
    ])

    # Max comparisons
    c_max_credit = df["customer_id"].map(cust_credit_max)
    c_max_debit = df["customer_id"].map(cust_debit_max)
    features.extend([
        (credit == c_max_credit).astype(int),
        (debit == c_max_debit).astype(int)
    ])

    # High amount indicators
    features.extend([
        (credit > np.where(c_avg_credit > 0, c_avg_credit * 2, 10000)).astype(int),
        (debit > np.where(c_avg_debit > 0, c_avg_debit * 2, 10000)).astype(int)
    ])

    # Balance deviation
    c_avg_bal = df["customer_id"].map(cust_balance_avg)
    features.extend([
        c_avg_bal,
        np.where(c_avg_bal > 0, (balance - c_avg_bal) / c_avg_bal, 0)
    ])

    print(f"Generated {len(features)} feature arrays for {len(df)} transactions")
    return np.column_stack(features)

def prepare_merged_features(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare combined KYC + Business features for merged model

    Args:
        df: DataFrame containing both KYC and business data

    Returns:
        numpy array of prepared features combining KYC and business features
    """
    kyc_features = prepare_kyc_features(df)
    business_features = prepare_business_features(df)

    print(f"KYC features shape: {kyc_features.shape}")
    print(f"Business features shape: {business_features.shape}")

    merged = np.column_stack([kyc_features, business_features])
    print(f"Merged features shape: {merged.shape}")

    return merged


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
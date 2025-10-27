# train_models.py
import numpy as np
import pandas as pd
import joblib
import gc
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

def safe_log1p(x):
    return np.log1p(np.clip(x, 0, None))

def prepare_kyc_features(df: pd.DataFrame) -> np.ndarray:
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
        "bachelors_degree": 5, "masters_degree": 6, "phd_and_above": 7
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
    features = []
    features.append(2024 - df["business_establishment_year"])
    sector_map = {"agriculture": 0, "manufacturing": 1, "domestic_trade_services": 2, "services": 3, "other": 4}
    features.append(df["business_sector"].astype(str).str.lower().map(sector_map).fillna(-1))
    level_map = {"growing": 0, "startup": 1}
    features.append(df["business_level"].astype(str).str.lower().map(level_map).fillna(-1))
    starting_cap = df["business_starting_capital"]
    current_cap = df["business_current_capital"]
    features.extend([starting_cap, current_cap, safe_log1p(starting_cap), safe_log1p(current_cap)])
    annual_profit = df["business_annual_profit"]
    annual_sales = df["business_annual_sales"]
    features.extend([annual_profit, annual_sales, safe_log1p(np.abs(annual_profit)), safe_log1p(annual_sales)])
    start_emp = df["business_starting_no_of_employees"]
    current_emp = df["business_current_no_of_employees"]
    features.extend([start_emp, current_emp])
    source_map = {"family": 0, "own": 1, "loan": 2, "fund": 3, "other": 4}
    features.append(df["business_source_of_initial_capital"].astype(str).str.lower().map(source_map).fillna(-1))
    assoc_map = {"sole_proprietorship": 0, "partnership": 1, "corporation": 2, "other": 3}
    features.append(df["business_association_type"].astype(str).str.lower().map(assoc_map).fillna(-1))
    features.append(np.where(starting_cap > 0, np.clip(current_cap / starting_cap, 0, 10), 0))
    features.append(np.where(start_emp > 0, np.clip(current_emp / start_emp, 0, 10), 0))
    features.append(np.where(annual_sales > 0, np.clip(annual_profit / annual_sales, -1, 1), 0))
    features.append(np.where(current_cap > 0, np.clip(annual_profit / current_cap, -1, 1), 0))
    features.append(safe_log1p(np.where(current_emp > 0, annual_sales / current_emp, 0)))
    features.append(np.where(current_cap > 0, annual_sales / current_cap, 0))
    cap_growth = features[-6]
    emp_growth = features[-5]
    features.append(np.abs(cap_growth - emp_growth))
    business_age = features[0]
    features.append(np.where(business_age > 0, safe_log1p(current_cap) / np.log1p(business_age + 1), 0))
    return np.column_stack(features)

def prepare_customer_features(df: pd.DataFrame, chunk_size: int = 1000) -> tuple[np.ndarray, list]:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    customer_ids = []
    customer_features = []
    customers = df["customer_id"].unique()
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
            # 🔥 NEW: Binary flags for round/night activity
            features.append(int((group["credit"] % 1000 == 0).any()))
            features.append(int(((group["date"].dt.hour >= 22) | (group["date"].dt.hour <= 6)).any()))
            features.append(int((narr.str.len() < 3).any()))
            lifetime = (group["date"].max() - group["date"].min()).days
            features.extend([lifetime, n_txns / max(lifetime, 1)])
            customer_features.append([float(x) if pd.notna(x) else 0.0 for x in features])
        del chunk_df
        gc.collect()
    X = np.array(customer_features, dtype=np.float32)
    return X, customer_ids

def prepare_transaction_features(df: pd.DataFrame, sample_frac: float = 1.0) -> np.ndarray:
    if sample_frac < 1.0:
        df = df.sample(frac=sample_frac, random_state=42)
    df = df.copy()
    features = []
    credit, debit, balance = df["credit"], df["debit"], df["closingBalance"]
    features.extend([credit, debit, balance, safe_log1p(credit), safe_log1p(debit), safe_log1p(balance)])
    source_map = {"cash deposit": 0, "fund transfer": 1, "cash withdraw": 2, "tele birr incoming": 3}
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
    hour, dow = df["date"].dt.hour, df["date"].dt.dayofweek
    features.extend([hour, dow])
    features.extend([
        ((hour >= 9) & (hour <= 17)).astype(int),
        ((hour >= 22) | (hour <= 6)).astype(int),
        (dow >= 5).astype(int)
    ])
    cust_txn_cnt = df.groupby("customer_id").size()
    cust_credit_sum = df.groupby("customer_id")["credit"].sum()
    cust_debit_sum = df.groupby("customer_id")["debit"].sum()
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
    c_avg_credit = df["customer_id"].map(cust_credit_sum / cust_txn_cnt)
    c_avg_debit = df["customer_id"].map(cust_debit_sum / cust_txn_cnt)
    features.extend([c_avg_credit, c_avg_debit])
    features.extend([
        np.where(c_avg_credit > 0, (credit - c_avg_credit) / c_avg_credit, 0),
        np.where(c_avg_debit > 0, (debit - c_avg_debit) / c_avg_debit, 0)
    ])
    c_max_credit = df.groupby("customer_id")["credit"].max()
    c_max_debit = df.groupby("customer_id")["debit"].max()
    features.extend([
        (credit == df["customer_id"].map(c_max_credit)).astype(int),
        (debit == df["customer_id"].map(c_max_debit)).astype(int)
    ])
    features.extend([
        (credit > np.where(c_avg_credit > 0, c_avg_credit * 2, 10000)).astype(int),
        (debit > np.where(c_avg_debit > 0, c_avg_debit * 2, 10000)).astype(int)
    ])
    c_avg_bal = df.groupby("customer_id")["closingBalance"].mean()
    features.extend([
        df["customer_id"].map(c_avg_bal),
        np.where(c_avg_bal > 0, (balance - df["customer_id"].map(c_avg_bal)) / df["customer_id"].map(c_avg_bal), 0)
    ])
    return np.column_stack(features)

def train_unsupervised_model(X: np.ndarray, model_type: str):
    print(f"Training {model_type.upper()} model...")
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    contamination = 0.02
    configs = {
        "customer": {"contamination": contamination, "n_estimators": 200, "max_samples": min(512, X.shape[0])},
        "transaction": {"contamination": contamination, "n_estimators": 150, "max_samples": 2048},
        "merged": {"contamination": contamination, "n_estimators": 175, "max_samples": 1024},
    }
    config = configs[model_type]
    model = IsolationForest(**config, random_state=42, n_jobs=-1)
    model.fit(X_scaled)
    return model, scaler

def train_all_models(data_dir="data/raw", models_dir="data/models"):
    Path(models_dir).mkdir(parents=True, exist_ok=True)
    # Merged
    df = pd.read_csv(Path(data_dir) / "kyc_business_training_data.csv")
    X = np.column_stack([prepare_kyc_features(df), prepare_business_features(df)])
    model, scaler = train_unsupervised_model(X, "merged")
    joblib.dump(model, Path(models_dir) / "merged_model.pkl")
    joblib.dump(scaler, Path(models_dir) / "merged_scaler.pkl")
    del df, X, model, scaler; gc.collect()
    # Transaction
    df = pd.read_csv(Path(data_dir) / "transaction_training_data.csv")
    X = prepare_transaction_features(df, sample_frac=0.3)
    model, scaler = train_unsupervised_model(X, "transaction")
    joblib.dump(model, Path(models_dir) / "transaction_model.pkl")
    joblib.dump(scaler, Path(models_dir) / "transaction_scaler.pkl")
    del df, X, model, scaler; gc.collect()
    # Customer
    df = pd.read_csv(Path(data_dir) / "transaction_training_data.csv")
    X, _ = prepare_customer_features(df, chunk_size=1000)
    model, scaler = train_unsupervised_model(X, "customer")
    joblib.dump(model, Path(models_dir) / "customer_model.pkl")
    joblib.dump(scaler, Path(models_dir) / "customer_scaler.pkl")
    print("✅ All models trained!")

if __name__ == "__main__":
    train_all_models()
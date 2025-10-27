"""
Feature Engineering Functions - EXACTLY as used in training
Copy from training scripts to ensure feature alignment
"""
import numpy as np
import pandas as pd


def safe_log1p(x):
    """Safe log1p that handles negative values"""
    return np.log1p(np.clip(x, 0, None))


def prepare_kyc_features(df: pd.DataFrame) -> np.ndarray:
    """
    Extract KYC features - EXACT as in training script
    Returns 13 features
    """
    features = []
    
    # 1. Demographics
    features.append(df["customer_age"])
    
    # 2. Gender (0=male, 1=female)
    gender = df["customer_gender"].astype(str).str.lower().str.contains("female").astype(int)
    features.append(gender)
    
    # 3. Marital status
    marital = df["customer_marital_status"].astype(str).str.lower()
    marital_map = {"single": 0, "unmarried": 0, "married": 1, "divorced": 2, "widowed": 3}
    features.append(marital.map(marital_map).fillna(-1))
    
    # 4. Education level
    education = df["customer_education_level"].astype(str).str.lower()
    edu_map = {
        "no_education_background": 0, "no_educational_background": 0,
        "primary": 1, "secondary": 2, "certificate": 3, "diploma": 4,
        "bachelors_degree": 5, "bachelor": 5, "masters_degree": 6,
        "master": 6, "phd_and_above": 7, "phd": 7
    }
    features.append(education.map(edu_map).fillna(-1))
    
    # 5-8. Location (categorical codes)
    features.append(pd.Categorical(df["customer_region"]).codes)
    features.append(pd.Categorical(df["customer_city"]).codes)
    features.append(pd.Categorical(df["customer_zone_or_sub_city"]).codes)
    features.append(pd.to_numeric(df["customer_woreda"], errors="coerce").fillna(0))
    
    # 9-10. Phone patterns
    phone_str = df["customer_phone_number"].astype(str)
    features.append(phone_str.str[-4:].astype(int))
    features.append(phone_str.apply(lambda x: len(set(x)) / len(x) if len(x) > 0 else 0))
    
    # 11-12. ID lengths
    features.append(df["customer_tin_number"].astype(str).str.len())
    features.append(df["customer_bank_account_number"].astype(str).str.len())
    
    # 13. Age-education ratio
    edu_encoded = features[3]
    features.append(np.where(edu_encoded > 0, df["customer_age"] / (edu_encoded + 1), 0))
    
    return np.column_stack(features)


def prepare_business_features(df: pd.DataFrame) -> np.ndarray:
    """
    Extract business features - EXACT as in training script
    Returns 23 features
    """
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
    features.extend([starting_cap, current_cap, safe_log1p(starting_cap), safe_log1p(current_cap)])
    
    # Financials
    annual_profit = df["business_annual_profit"]
    annual_sales = df["business_annual_sales"]
    features.extend([annual_profit, annual_sales, safe_log1p(np.abs(annual_profit)), safe_log1p(annual_sales)])
    
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
    features.append(safe_log1p(np.where(current_emp > 0, annual_sales / current_emp, 0)))
    features.append(np.where(current_cap > 0, annual_sales / current_cap, 0))
    
    # Consistency checks
    cap_growth = features[-6]
    emp_growth = features[-5]
    features.append(np.abs(cap_growth - emp_growth))
    
    business_age = features[0]
    features.append(np.where(business_age > 0, safe_log1p(current_cap) / np.log1p(business_age + 1), 0))
    
    return np.column_stack(features)


def prepare_combined_features(df: pd.DataFrame) -> np.ndarray:
    """
    Combine KYC and business features
    Returns 36 features (13 KYC + 23 business)
    """
    kyc_features = prepare_kyc_features(df)
    business_features = prepare_business_features(df)
    return np.column_stack([kyc_features, business_features])


def prepare_customer_features(df: pd.DataFrame) -> np.ndarray:
    """
    Extract customer-level aggregated features from transaction data
    Exactly as in training script - returns customer features per customer_id
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    
    customer_ids = []
    customer_features = []
    
    for customer_id, group in df.groupby("customer_id"):
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
    
    return np.array(customer_features, dtype=np.float32)


# DataFrame wrapper functions for compatibility
def prepare_kyc_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """Wrapper for KYC features"""
    return prepare_kyc_features(df)


def prepare_business_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """Wrapper for business features"""
    return prepare_business_features(df)


def prepare_combined_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """Wrapper for combined features"""
    return prepare_combined_features(df)


def prepare_customer_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """Wrapper for customer features"""
    return prepare_customer_features(df)


def prepare_transaction_features(df: pd.DataFrame) -> np.ndarray:
    """
    Extract transaction features - EXACT as in training script
    Transaction-level features including amounts, temporal patterns, and customer aggregations
    """
    df = df.copy()
    features = []

    # Basic amounts (6 features)
    credit, debit, balance = df["credit"], df["debit"], df["closingBalance"]
    features.extend([credit, debit, balance, np.log1p(credit), np.log1p(debit), np.log1p(balance)])

    # Source encoding (1 feature)
    source_map = {"cash deposit": 0, "fund transfer": 1, "cash withdraw": 2,
                  "tele birr incoming": 3, "tele birr out going": 4, "atm card subscription fee": 5}
    features.append(df["source"].str.lower().map(source_map).fillna(-1))

    # Source indicators (4 features)
    src = df["source"].str.lower().fillna("")
    features.extend([
        src.str.contains("cash deposit").astype(int),
        src.str.contains("fund transfer").astype(int),
        src.str.contains("cash withdraw").astype(int),
        src.str.contains("tele birr").astype(int)
    ])

    # Narrative (2 features)
    narr = df["narrative"].fillna("")
    features.extend([narr.str.len(), (narr.str.len() < 5).astype(int)])

    # Transaction amounts (4 features)
    txn_amt = credit - debit
    features.extend([txn_amt, np.abs(txn_amt)])
    features.extend([
        np.clip(np.where(balance > 0, txn_amt / balance, 0), -10, 10),
        np.clip(np.where(balance > 0, np.abs(txn_amt) / balance, 0), 0, 10)
    ])

    # Round amounts (3 features)
    features.extend([
        (credit % 1000 == 0).astype(int),
        (debit % 1000 == 0).astype(int),
        ((credit % 1000 == 0) | (debit % 1000 == 0)).astype(int)
    ])

    # Temporal (8 features)
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

    # Map to transactions (3 features)
    txn_freq = df["customer_id"].map(cust_txn_cnt)
    features.extend([txn_freq, np.log1p(txn_freq)])

    c_credit_tot = df["customer_id"].map(cust_credit_sum)
    c_debit_tot = df["customer_id"].map(cust_debit_sum)
    features.extend([c_credit_tot, c_debit_tot, np.log1p(c_credit_tot / (c_debit_tot + 1))])

    # Transaction as percentage of customer total (2 features)
    features.extend([
        np.where(c_credit_tot > 0, credit / c_credit_tot, 0),
        np.where(c_debit_tot > 0, debit / c_debit_tot, 0)
    ])

    # Daily velocity (2 features)
    daily_cnt = df.groupby(["customer_id", df["date"].dt.date]).size()
    df["daily_vel"] = df.set_index(["customer_id", df["date"].dt.date]).index.map(daily_cnt).fillna(1)
    features.extend([df["daily_vel"], (df["daily_vel"] > 5).astype(int)])

    # Customer averages (2 features)
    c_avg_credit = df["customer_id"].map(cust_credit_avg)
    c_avg_debit = df["customer_id"].map(cust_debit_avg)
    features.extend([c_avg_credit, c_avg_debit])

    # Deviations (2 features)
    features.extend([
        np.where(c_avg_credit > 0, (credit - c_avg_credit) / c_avg_credit, 0),
        np.where(c_avg_debit > 0, (debit - c_avg_debit) / c_avg_debit, 0)
    ])

    # Max comparisons (2 features)
    c_max_credit = df["customer_id"].map(cust_credit_max)
    c_max_debit = df["customer_id"].map(cust_debit_max)
    features.extend([
        (credit == c_max_credit).astype(int),
        (debit == c_max_debit).astype(int)
    ])

    # High amount indicators (2 features)
    features.extend([
        (credit > np.where(c_avg_credit > 0, c_avg_credit * 2, 10000)).astype(int),
        (debit > np.where(c_avg_debit > 0, c_avg_debit * 2, 10000)).astype(int)
    ])

    # Balance deviation (2 features)
    c_avg_bal = df["customer_id"].map(cust_balance_avg)
    features.extend([
        c_avg_bal,
        np.where(c_avg_bal > 0, (balance - c_avg_bal) / c_avg_bal, 0)
    ])

    print(f"Generated {len(features)} feature arrays for {len(df)} transactions")
    return np.column_stack(features)


def prepare_transaction_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """Wrapper for transaction features"""
    return prepare_transaction_features(df)



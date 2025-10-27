import pandas as pd
import numpy as np

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
        
        features.append(n_txns)
        features.append(np.log1p(n_txns))
        
        credit_sum = group["credit"].sum()
        debit_sum = group["debit"].sum()
        features.extend([
            credit_sum, debit_sum,
            group["credit"].mean(), group["debit"].mean(),
            group["credit"].max(), group["debit"].max(),
            group["credit"].std() if n_txns > 1 else 0.0,
            group["debit"].std() if n_txns > 1 else 0.0
        ])
        
        cd_ratio = credit_sum / (debit_sum + 1)
        features.append(np.log1p(cd_ratio))
        
        balance = group["closingBalance"]
        features.extend([
            balance.mean(), balance.max(), balance.min(),
            balance.std() if n_txns > 1 else 0.0
        ])
        
        txn_amt = group["credit"] - group["debit"]
        features.extend([
            txn_amt.mean(), txn_amt.max(), txn_amt.min(),
            txn_amt.std() if n_txns > 1 else 0.0,
            txn_amt.median()
        ])
        
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

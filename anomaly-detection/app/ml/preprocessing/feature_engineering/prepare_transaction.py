import pandas as pd
import numpy as np

def prepare_transaction_features(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare transaction-level features with advanced behavior patterns
    Similar logic to customer-level features but applied to individual transactions
    """
    features = []
    df = df.copy()
    
    # Basic transaction amounts
    credit = df["credit"].values
    debit = df["debit"].values
    balance = df["closingBalance"].values
    
    # Raw values
    features.extend([credit, debit, balance])
    
    # Log transformations for better scaling
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
    
    # Source-specific indicators (one-hot style)
    source_lower = df["source"].str.lower().fillna("")
    is_cash_deposit = source_lower.str.contains("cash deposit").astype(int).values
    is_fund_transfer = source_lower.str.contains("fund transfer").astype(int).values
    is_cash_withdraw = source_lower.str.contains("cash withdraw").astype(int).values
    is_tele_birr = source_lower.str.contains("tele birr").astype(int).values
    features.extend([is_cash_deposit, is_fund_transfer, is_cash_withdraw, is_tele_birr])
    
    # Narrative features
    narrative = df["narrative"].fillna("")
    narrative_length = narrative.str.len().values
    features.append(narrative_length)
    
    # Short narrative indicator (potential fraud signal)
    is_short_narrative = (narrative.str.len() < 5).astype(int).values
    features.append(is_short_narrative)
    
    # Transaction amount (net flow)
    transaction_amount = credit - debit
    features.append(transaction_amount)
    features.append(np.abs(transaction_amount))
    
    # Balance ratio (transaction impact on balance)
    balance_ratio = np.where(balance > 0, transaction_amount / balance, 0)
    features.append(np.clip(balance_ratio, -10, 10))
    
    # Balance ratio for absolute amount
    abs_balance_ratio = np.where(balance > 0, np.abs(transaction_amount) / balance, 0)
    features.append(np.clip(abs_balance_ratio, 0, 10))
    
    # Round amount detection (fraud indicator)
    is_round_credit = (credit % 1000 == 0).astype(int)
    is_round_debit = (debit % 1000 == 0).astype(int)
    is_round_amount = ((credit % 1000 == 0) | (debit % 1000 == 0)).astype(int)
    features.extend([is_round_credit, is_round_debit, is_round_amount])
    
    # Temporal features
    df["date"] = pd.to_datetime(df["date"])
    hour = df["date"].dt.hour.values
    dayofweek = df["date"].dt.dayofweek.values
    day = df["date"].dt.day.values
    month = df["date"].dt.month.values
    
    features.extend([hour, dayofweek, day, month])
    
    # Business hours indicator
    is_business_hours = ((hour >= 9) & (hour <= 17)).astype(int)
    features.append(is_business_hours)
    
    # Night transaction indicator (suspicious timing)
    is_night_transaction = ((hour >= 22) | (hour <= 6)).astype(int)
    features.append(is_night_transaction)
    
    # Weekend indicator
    is_weekend = (dayofweek >= 5).astype(int)
    features.append(is_weekend)
    
    # Weekday indicator
    is_weekday = (dayofweek < 5).astype(int)
    features.append(is_weekday)
    
    # Customer-level aggregations
    customer_txn_counts = df.groupby("customer_id").size()
    txn_freq = df["customer_id"].map(customer_txn_counts).values
    features.append(txn_freq)
    features.append(np.log1p(txn_freq))
    
    # Customer's total credit/debit
    customer_total_credit = df.groupby("customer_id")["credit"].sum()
    customer_total_debit = df.groupby("customer_id")["debit"].sum()
    customer_credit_total = df["customer_id"].map(customer_total_credit).values
    customer_debit_total = df["customer_id"].map(customer_total_debit).values
    features.extend([customer_credit_total, customer_debit_total])
    
    # Credit/Debit ratio for customer
    cd_ratio = customer_credit_total / (customer_debit_total + 1)
    features.append(np.log1p(cd_ratio))
    
    # Transaction as percentage of customer's total activity
    txn_pct_of_customer_credit = np.where(customer_credit_total > 0, 
                                          credit / customer_credit_total, 0)
    txn_pct_of_customer_debit = np.where(customer_debit_total > 0,
                                         debit / customer_debit_total, 0)
    features.extend([txn_pct_of_customer_credit, txn_pct_of_customer_debit])
    
    # Daily velocity (transactions per day)
    df["date_only"] = df["date"].dt.date
    daily_txn_count = df.groupby(["customer_id", "date_only"]).size()
    df["daily_velocity"] = df.set_index(["customer_id", "date_only"]).index.map(daily_txn_count.to_dict())
    daily_velocity = df["daily_velocity"].fillna(1).values
    features.append(daily_velocity)
    
    # High velocity indicator (burst detection)
    is_high_velocity = (daily_velocity > 5).astype(int)
    features.append(is_high_velocity)
    
    # Customer's average transaction amounts
    customer_avg_credit = df.groupby("customer_id")["credit"].mean()
    customer_avg_debit = df.groupby("customer_id")["debit"].mean()
    avg_customer_credit = df["customer_id"].map(customer_avg_credit).values
    avg_customer_debit = df["customer_id"].map(customer_avg_debit).values
    features.extend([avg_customer_credit, avg_customer_debit])
    
    # Deviation from customer's average (anomaly indicator)
    credit_deviation = np.where(avg_customer_credit > 0,
                               (credit - avg_customer_credit) / avg_customer_credit, 0)
    debit_deviation = np.where(avg_customer_debit > 0,
                              (debit - avg_customer_debit) / avg_customer_debit, 0)
    features.extend([credit_deviation, debit_deviation])
    
    # Customer's max transaction amounts
    customer_max_credit = df.groupby("customer_id")["credit"].max()
    customer_max_debit = df.groupby("customer_id")["debit"].max()
    max_customer_credit = df["customer_id"].map(customer_max_credit).values
    max_customer_debit = df["customer_id"].map(customer_max_debit).values
    
    # Is this transaction at or near customer's max?
    is_max_credit = (credit == max_customer_credit).astype(int)
    is_max_debit = (debit == max_customer_debit).astype(int)
    features.extend([is_max_credit, is_max_debit])
    
    # High amount indicator (transaction is in top 10% for customer)
    credit_threshold = np.where(avg_customer_credit > 0, avg_customer_credit * 2, 10000)
    debit_threshold = np.where(avg_customer_debit > 0, avg_customer_debit * 2, 10000)
    is_high_credit = (credit > credit_threshold).astype(int)
    is_high_debit = (debit > debit_threshold).astype(int)
    features.extend([is_high_credit, is_high_debit])
    
    # Customer's balance statistics
    customer_avg_balance = df.groupby("customer_id")["closingBalance"].mean()
    avg_customer_balance = df["customer_id"].map(customer_avg_balance).values
    features.append(avg_customer_balance)
    
    # Balance deviation
    balance_deviation = np.where(avg_customer_balance > 0,
                                (balance - avg_customer_balance) / avg_customer_balance, 0)
    features.append(balance_deviation)
    
    print(f"Generated {len(features)} feature arrays for {len(df)} transactions")
    return np.column_stack(features)

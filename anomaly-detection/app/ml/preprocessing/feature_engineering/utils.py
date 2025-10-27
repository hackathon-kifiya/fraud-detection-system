"""
Feature Engineering Utilities
Handles feature preparation and transformation for different data types
"""
import numpy as np
import pandas as pd

from app.core.logging import get_logger

logger = get_logger(__name__)


def prepare_kyc_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare KYC features from DataFrame (matching training script)

    Args:
        df: DataFrame containing KYC data

    Returns:
        numpy array of prepared features
    """
    features = []

    features.append(df["customer_age"].values)

    # Handle gender - remove "Gender." prefix if present
    gender_col = (
        df["customer_gender"]
        .astype(str)
        .str.replace("Gender.", "", regex=False)
        .str.lower()
    )
    gender_encoded = (gender_col == "female").astype(int)
    features.append(gender_encoded.values)

    # Handle marital status - remove prefix
    marital_col = (
        df["customer_marital_status"]
        .astype(str)
        .str.replace("MaritalStatusOptions.", "", regex=False)
        .str.lower()
    )
    marital_mapping = {"single": 0, "married": 1, "divorced": 2, "widowed": 3}
    marital_encoded = marital_col.map(marital_mapping).fillna(-1)
    features.append(marital_encoded.values)

    # Handle education level - remove prefix
    education_col = (
        df["customer_education_level"]
        .astype(str)
        .str.replace("EducationalLevelOptions.", "", regex=False)
        .str.lower()
    )
    education_mapping = {
        "primary": 0,
        "secondary": 1,
        "tertiary": 2,
        "post_graduate": 3,
    }
    education_encoded = education_col.map(education_mapping).fillna(-1)
    features.append(education_encoded.values)

    region_encoded = pd.Categorical(df["customer_region"]).codes
    features.append(region_encoded)

    city_encoded = pd.Categorical(df["customer_city"]).codes
    features.append(city_encoded)

    zone_encoded = pd.Categorical(df["customer_zone_or_sub_city"]).codes
    features.append(zone_encoded)

    woreda_numeric = pd.to_numeric(df["customer_woreda"], errors="coerce").fillna(0)
    features.append(woreda_numeric.values)

    phone_last_4 = df["customer_phone_number"].astype(str).str[-4:].astype(int)
    features.append(phone_last_4.values)

    tin_length = df["customer_tin_number"].astype(str).str.len()
    features.append(tin_length.values)

    account_length = df["customer_bank_account_number"].astype(str).str.len()
    features.append(account_length.values)

    return np.column_stack(features)


def prepare_transaction_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare transaction features from DataFrame (matching training script)

    Args:
        df: DataFrame containing transaction data

    Returns:
        numpy array of prepared features
    """
    features = []

    features.append(df["credit"].values)
    features.append(df["debit"].values)
    features.append(df["closingBalance"].values)

    source_mapping = {
        "CASH DEPOSIT": 0,
        "FUND TRANSFER": 1,
        "CASH WITHDRAW": 2,
        "TELE BIRR INCOMING": 3,
        "TELE BIRR OUT GOING": 4,
        "ATM card subscription fee": 5,
    }
    source_encoded = df["source"].map(source_mapping).fillna(-1)
    features.append(source_encoded.values)

    narrative_length = df["narrative"].str.len()
    features.append(narrative_length.values)

    transaction_amount = df["credit"] - df["debit"]
    features.append(transaction_amount.values)

    balance_ratio = np.where(
        df["closingBalance"] > 0, transaction_amount / df["closingBalance"], 0
    )
    features.append(balance_ratio)

    df["date"] = pd.to_datetime(df["date"])
    features.append(df["date"].dt.hour.values)
    features.append(df["date"].dt.dayofweek.values)
    features.append(df["date"].dt.day.values)
    features.append(df["date"].dt.month.values)

    customer_txn_counts = df.groupby("customer_id").size()
    features.append(df["customer_id"].map(customer_txn_counts).values)

    return np.column_stack(features)


def prepare_business_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare business features from DataFrame (matching training script)

    Args:
        df: DataFrame containing business data

    Returns:
        numpy array of prepared features
    """
    features = []

    features.append(df["business_establishment_year"].values)

    sector_mapping = {
        "AGRICULTURE": 0,
        "MANUFACTURING": 1,
        "DOMESTIC_TRADE_SERVICES": 2,
        "SERVICES": 3,
        "OTHER": 4,
    }
    sector_encoded = df["business_sector"].map(sector_mapping).fillna(-1)
    features.append(sector_encoded.values)

    level_mapping = {"GROWING": 0, "STARTUP": 1}
    level_encoded = df["business_level"].map(level_mapping).fillna(-1)
    features.append(level_encoded.values)

    features.append(df["business_starting_capital"].values)
    features.append(df["business_current_capital"].values)
    features.append(df["business_annual_profit"].values)
    features.append(df["business_annual_sales"].values)
    features.append(df["business_starting_no_of_employees"].values)
    features.append(df["business_current_no_of_employees"].values)

    source_mapping = {"FAMILY": 0, "OWN": 1, "LOAN": 2, "FUND": 3, "OTHER": 4}
    source_encoded = (
        df["business_source_of_initial_capital"].map(source_mapping).fillna(-1)
    )
    features.append(source_encoded.values)

    association_mapping = {
        "SOLE_PROPRIETORSHIP": 0,
        "PARTNERSHIP": 1,
        "CORPORATION": 2,
        "OTHER": 3,
    }
    association_encoded = (
        df["business_association_type"].map(association_mapping).fillna(-1)
    )
    features.append(association_encoded.values)

    capital_growth = np.where(
        df["business_starting_capital"] > 0,
        df["business_current_capital"] / df["business_starting_capital"],
        0,
    )
    features.append(capital_growth)

    employee_growth = np.where(
        df["business_starting_no_of_employees"] > 0,
        df["business_current_no_of_employees"]
        / df["business_starting_no_of_employees"],
        0,
    )
    features.append(employee_growth)

    profit_margin = np.where(
        df["business_annual_sales"] > 0,
        df["business_annual_profit"] / df["business_annual_sales"],
        0,
    )
    features.append(profit_margin)

    current_year = 2024
    business_age = current_year - df["business_establishment_year"]
    features.append(business_age.values)

    return np.column_stack(features)


def prepare_combined_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare combined KYC + Business features from DataFrame

    Args:
        df: DataFrame containing both KYC and business data

    Returns:
        numpy array of prepared features
    """
    kyc_features = prepare_kyc_features_from_df(df)
    business_features = prepare_business_features_from_df(df)
    return np.column_stack([kyc_features, business_features])


def prepare_customer_features_from_df(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare customer-level features from transaction DataFrame
    MUST match training_features.py exactly for consistency
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
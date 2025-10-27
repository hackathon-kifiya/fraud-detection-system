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

    Args:
        df: DataFrame containing transaction data

    Returns:
        numpy array of prepared customer features
    """
    customer_features = []

    for _, customer_df in df.groupby("customer_id"):
        features = []

        total_transactions = len(customer_df)
        features.append(total_transactions)

        total_credit = customer_df["credit"].sum()
        total_debit = customer_df["debit"].sum()
        avg_credit = customer_df["credit"].mean()
        avg_debit = customer_df["debit"].mean()
        max_credit = customer_df["credit"].max()
        max_debit = customer_df["debit"].max()
        features.extend(
            [
                total_credit,
                total_debit,
                avg_credit,
                avg_debit,
                max_credit,
                max_debit,
            ]
        )

        avg_balance = customer_df["closingBalance"].mean()
        max_balance = customer_df["closingBalance"].max()
        min_balance = customer_df["closingBalance"].min()
        balance_volatility = customer_df["closingBalance"].std()
        features.extend([avg_balance, max_balance, min_balance, balance_volatility])

        transaction_amounts = customer_df["credit"] - customer_df["debit"]
        features.extend(
            [
                transaction_amounts.mean(),
                transaction_amounts.max(),
                transaction_amounts.min(),
                transaction_amounts.std(),
            ]
        )

        source_counts = customer_df["source"].value_counts()
        unique_sources = len(source_counts)
        most_common_source_ratio = (
            source_counts.iloc[0] / total_transactions if total_transactions > 0 else 0
        )

        cash_deposit_ratio = (
            customer_df["source"] == "CASH DEPOSIT"
        ).sum() / total_transactions
        fund_transfer_ratio = (
            customer_df["source"] == "FUND TRANSFER"
        ).sum() / total_transactions
        cash_withdraw_ratio = (
            customer_df["source"] == "CASH WITHDRAW"
        ).sum() / total_transactions
        tele_birr_ratio = (
            (customer_df["source"] == "TELE BIRR INCOMING")
            | (customer_df["source"] == "TELE BIRR OUT GOING")
        ).sum() / total_transactions

        features.extend(
            [
                unique_sources,
                most_common_source_ratio,
                cash_deposit_ratio,
                fund_transfer_ratio,
                cash_withdraw_ratio,
                tele_birr_ratio,
            ]
        )

        customer_df["date"] = pd.to_datetime(customer_df["date"])
        avg_hour = customer_df["date"].dt.hour.mean()
        hour_std = customer_df["date"].dt.hour.std()
        night_transactions = (
            (customer_df["date"].dt.hour >= 22) | (customer_df["date"].dt.hour <= 6)
        ).sum() / total_transactions
        features.extend([avg_hour, hour_std, night_transactions])

        weekday_transactions = (
            customer_df["date"].dt.dayofweek < 5
        ).sum() / total_transactions
        weekend_transactions = (
            customer_df["date"].dt.dayofweek >= 5
        ).sum() / total_transactions
        features.extend([weekday_transactions, weekend_transactions])

        if total_transactions > 1:
            time_diffs = (
                customer_df["date"].sort_values().diff().dt.total_seconds() / 3600
            )
            features.extend([time_diffs.mean(), time_diffs.min(), time_diffs.max()])
        else:
            features.extend([0, 0, 0])

        avg_narrative_length = customer_df["narrative"].str.len().mean()
        unique_narratives = customer_df["narrative"].nunique()
        narrative_diversity = unique_narratives / total_transactions
        features.extend([avg_narrative_length, unique_narratives, narrative_diversity])

        balance_ratios = np.where(
            customer_df["closingBalance"] > 0,
            transaction_amounts / customer_df["closingBalance"],
            0,
        )
        features.extend(
            [balance_ratios.mean(), balance_ratios.max(), balance_ratios.std()]
        )

        high_amount_transactions = (
            np.abs(transaction_amounts) > transaction_amounts.quantile(0.9)
        ).sum() / total_transactions
        rapid_transactions = (
            (time_diffs < 1).sum() / max(total_transactions - 1, 1)
            if total_transactions > 1
            else 0
        )
        features.extend([high_amount_transactions, rapid_transactions])

        customer_features.append(features)

    return np.array(customer_features)
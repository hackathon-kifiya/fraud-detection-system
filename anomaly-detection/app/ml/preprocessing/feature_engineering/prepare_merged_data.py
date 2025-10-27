import pandas as pd
import numpy as np


def prepare_kyc_features(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare KYC features from DataFrame for merged model
    Enhanced with more anomaly detection signals
    
    Args:
        df: DataFrame containing KYC data
        
    Returns:
        numpy array of prepared features
    """
    features = []
    
    # Basic demographics
    age = df["customer_age"].values
    features.append(age)
    
    # Gender encoding
    gender_col = (
        df["customer_gender"]
        .astype(str)
        .str.replace("Gender.", "", regex=False)
        .str.lower()
    )
    gender_encoded = (gender_col == "female").astype(int)
    features.append(gender_encoded.values)
    
    # Marital status encoding
    marital_col = (
        df["customer_marital_status"]
        .astype(str)
        .str.replace("MaritalStatusOptions.", "", regex=False)
        .str.lower()
    )
    marital_mapping = {
        "single": 0, "unmarried": 0,  # Combined
        "married": 1, 
        "divorced": 2, 
        "widowed": 3
    }
    marital_encoded = marital_col.map(marital_mapping).fillna(-1)
    features.append(marital_encoded.values)
    
    # Education level encoding
    education_col = (
        df["customer_education_level"]
        .astype(str)
        .str.replace("EducationalLevelOptions.", "", regex=False)
        .str.lower()
    )
    education_mapping = {
        "no_education_background": 0,
        "primary": 1,
        "secondary": 2,
        "certificate": 3,
        "diploma": 4,
        "bachelors_degree": 5,
        "bachelor": 5,  # Alias
        "masters_degree": 6,
        "master": 6,  # Alias
        "phd_and_above": 7,
        "phd": 7,  # Alias
        "tertiary": 4,  # Map to diploma
        "post_graduate": 6  # Map to masters
    }
    education_encoded = education_col.map(education_mapping).fillna(-1)
    features.append(education_encoded.values)
    
    # Location features
    region_encoded = pd.Categorical(df["customer_region"]).codes
    features.append(region_encoded)
    
    city_encoded = pd.Categorical(df["customer_city"]).codes
    features.append(city_encoded)
    
    zone_encoded = pd.Categorical(df["customer_zone_or_sub_city"]).codes
    features.append(zone_encoded)
    
    woreda_numeric = pd.to_numeric(df["customer_woreda"], errors="coerce").fillna(0)
    features.append(woreda_numeric.values)
    
    # Phone number patterns
    phone_last_4 = df["customer_phone_number"].astype(str).str[-4:].astype(int)
    features.append(phone_last_4.values)
    
    # Phone number entropy (repetitive digits = suspicious)
    phone_str = df["customer_phone_number"].astype(str)
    phone_entropy = phone_str.apply(lambda x: len(set(x)) / len(x) if len(x) > 0 else 0)
    features.append(phone_entropy.values)
    
    # TIN and Account patterns
    tin_length = df["customer_tin_number"].astype(str).str.len()
    features.append(tin_length.values)
    
    account_length = df["customer_bank_account_number"].astype(str).str.len()
    features.append(account_length.values)
    
    # Age-education consistency check
    age_edu_ratio = np.where(education_encoded > 0, age / (education_encoded + 1), 0)
    features.append(age_edu_ratio)
    
    return np.column_stack(features)


def prepare_business_features(df: pd.DataFrame) -> np.ndarray:
    """
    Prepare business features from DataFrame for merged model
    Enhanced with financial ratios and growth indicators
    
    Args:
        df: DataFrame containing business data
        
    Returns:
        numpy array of prepared features
    """
    features = []
    
    # Basic info
    current_year = 2024
    business_age = (current_year - df["business_establishment_year"]).values
    features.append(business_age)
    
    # Sector encoding
    sector_col = (
        df["business_sector"]
        .astype(str)
        .str.lower()
    )
    sector_mapping = {
        "agriculture": 0, 
        "manufacturing": 1, 
        "domestic_trade_services": 2, 
        "services": 3, 
        "other": 4
    }
    sector_encoded = sector_col.map(sector_mapping).fillna(-1)
    features.append(sector_encoded.values)
    
    # Business level encoding
    level_col = df["business_level"].astype(str).str.lower()
    level_mapping = {"growing": 0, "startup": 1}
    level_encoded = level_col.map(level_mapping).fillna(-1)
    features.append(level_encoded.values)
    
    # Capital features
    starting_cap = df["business_starting_capital"].values
    current_cap = df["business_current_capital"].values
    features.extend([starting_cap, current_cap])
    
    # Log-transformed capital (better for extreme values)
    features.append(np.log1p(starting_cap))
    features.append(np.log1p(current_cap))
    
    # Financial metrics
    annual_profit = df["business_annual_profit"].values
    annual_sales = df["business_annual_sales"].values
    features.extend([annual_profit, annual_sales])
    
    # Log-transformed financials
    features.append(np.log1p(annual_profit))
    features.append(np.log1p(annual_sales))
    
    # Employee counts
    start_employees = df["business_starting_no_of_employees"].values
    current_employees = df["business_current_no_of_employees"].values
    features.extend([start_employees, current_employees])
    
    # Source of capital encoding
    source_col = df["business_source_of_initial_capital"].astype(str).str.lower()
    source_mapping = {"family": 0, "own": 1, "loan": 2, "fund": 3, "other": 4}
    source_encoded = source_col.map(source_mapping).fillna(-1)
    features.append(source_encoded.values)
    
    # Association type encoding
    association_col = df["business_association_type"].astype(str).str.lower()
    association_mapping = {
        "sole_proprietorship": 0, 
        "partnership": 1, 
        "corporation": 2, 
        "other": 3
    }
    association_encoded = association_col.map(association_mapping).fillna(-1)
    features.append(association_encoded.values)
    
    # ENHANCED DERIVED FEATURES
    # Capital growth (with clipping to prevent extreme values)
    capital_growth = np.where(starting_cap > 0, np.clip(current_cap / starting_cap, 0, 10), 0)
    features.append(capital_growth)
    
    # Employee growth
    employee_growth = np.where(start_employees > 0, np.clip(current_employees / start_employees, 0, 10), 0)
    features.append(employee_growth)
    
    # Profit margin
    profit_margin = np.where(annual_sales > 0, np.clip(annual_profit / annual_sales, -1, 1), 0)
    features.append(profit_margin)
    
    # Return on capital
    roc = np.where(current_cap > 0, np.clip(annual_profit / current_cap, -1, 1), 0)
    features.append(roc)
    
    # Employee productivity (sales per employee)
    emp_productivity = np.where(current_employees > 0, annual_sales / current_employees, 0)
    features.append(np.log1p(emp_productivity))
    
    # Capital efficiency (sales per unit capital)
    cap_efficiency = np.where(current_cap > 0, annual_sales / current_cap, 0)
    features.append(cap_efficiency)
    
    # Growth consistency check (mismatch between capital and employee growth)
    growth_mismatch = np.abs(capital_growth - employee_growth)
    features.append(growth_mismatch)
    
    # Age-appropriate capital check
    age_cap_ratio = np.where(business_age > 0, np.log1p(current_cap) / np.log1p(business_age + 1), 0)
    features.append(age_cap_ratio)
    
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


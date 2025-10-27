import os
import sys
from enum import Enum
from pathlib import Path
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator

# --- Enums ---
class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
class MaritalStatusOptions(str, Enum):
    MARRIED = "MARRIED"
    UNMARRIED = "UNMARRIED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"
class EducationalLevelOptions(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    CERTIFICATE = "CERTIFICATE"
    DIPLOMA = "DIPLOMA"
    BACHELORS_DEGREE = "BACHELORS_DEGREE"
    MASTERS_DEGREE = "MASTERS_DEGREE"
    PHD_AND_ABOVE = "PHD_AND_ABOVE"
    NO_EDUCATIONAL_BACKGROUND = "NO_EDUCATIONAL_BACKGROUND"
class Region(str, Enum):
    ADDIS_ABABA = "ADDIS_ABABA"
    AFAR = "AFAR"
    TIGRAY = "TIGRAY"
    AMHARA = "AMHARA"
    BENISHANGUL_GUMUZ = "BENISHANGUL_GUMUZ"
    GAMBELA = "GAMBELA"
    OROMIA = "OROMIA"
    SIDAMA = "SIDAMA"
    SOMALI = "SOMALI"
    SNNP = "SNNP"
    HARAR = "HARAR"
    DIRE_DAWA = "DIRE_DAWA"
    SWEP = "SWEP"
class City(str, Enum):
    ADDIS_ABABA = "ADDIS_ABABA"
    BAHIR_DAR = "BAHIR_DAR"
    DERBA = "DERBA"
    GONDAR = "GONDAR"
    HARRAR = "HARRAR"
    JIMMA = "JIMMA"
    LALIBELA = "LALIBELA"
    MEKELLE = "MEKELLE"
class ZoneOrSubCity(str, Enum):
    BOLE = "BOLE"
    ARADA = "ARADA"
    GULELE = "GULELE"
    ZONE_1 = "ZONE_1"
    ZONE_2 = "ZONE_2"
    ZONE_3 = "ZONE_3"
    ZONE_4 = "ZONE_4"
    ZONE_5 = "ZONE_5"
    ZONE_6 = "ZONE_6"
    ZONE_7 = "ZONE_7"
    ZONE_8 = "ZONE_8"
    ZONE_9 = "ZONE_9"
    ZONE_10 = "ZONE_10"
    ZONE_11 = "ZONE_11"
    ZONE_12 = "ZONE_12"
    ZONE_13 = "ZONE_13"
class SourceOfInitialCapital(str, Enum):
    FAMILY = "FAMILY"
    OWN = "OWN"
    LOAN = "LOAN"
    FUND = "FUND"
    OTHER = "OTHER"
class AssociationType(str, Enum):
    SOLE_PROPRIETORSHIP = "SOLE_PROPRIETORSHIP"
    PARTNERSHIP = "PARTNERSHIP"
    CORPORATION = "CORPORATION"
    OTHER = "OTHER"
class BusinessSector(str, Enum):
    AGRICULTURE = "AGRICULTURE"
    MANUFACTURING = "MANUFACTURING"
    DOMESTIC_TRADE_SERVICES = "DOMESTIC_TRADE_SERVICES"
    SERVICES = "SERVICES"
    OTHER = "OTHER"
class BusinessLevel(str, Enum):
    GROWING = "GROWING"
    STARTUP = "STARTUP"

# --- Pydantic Models ---
class CustomerKYC(BaseModel):
    customer_phone_number: int = Field(..., ge=900000000, le=999999999)
    customer_age: int = Field(..., ge=0, le=130)
    customer_gender: Gender
    customer_marital_status: MaritalStatusOptions
    customer_education_level: EducationalLevelOptions
    customer_tin_number: str
    customer_name: str
    customer_bank_account_number: str
    customer_region: Region
    customer_city: City
    customer_zone_or_sub_city: ZoneOrSubCity
    customer_woreda: str
    customerId: str
    @field_validator("customer_tin_number")
    def validate_tin(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError("TIN must be 10 digits")
        return v
    @field_validator("customer_bank_account_number")
    def validate_account(cls, v):
        if len(v) != 13 or not v.isdigit():
            raise ValueError("Bank account must be 13 digits")
        return v
    @field_validator("customer_woreda")
    def validate_woreda(cls, v):
        if not v.isdigit() or not (1 <= int(v) <= 15):
            raise ValueError("Woreda must be integer 1–15")
        return v

class BusinessInformation(BaseModel):
    business_establishment_year: int = Field(..., ge=1800, le=2035)
    business_sector: BusinessSector
    business_level: BusinessLevel
    business_tin_number: str
    business_region: Region
    business_city: City
    business_subcity: City
    business_woreda: str
    business_zone_or_sub_city: ZoneOrSubCity
    business_starting_capital: float = Field(..., ge=0)
    business_current_capital: float = Field(..., ge=0)
    business_annual_profit: float
    business_annual_sales: float = Field(..., ge=0)
    business_starting_no_of_employees: int = Field(..., ge=0)
    business_current_no_of_employees: int = Field(..., ge=0)
    business_source_of_initial_capital: SourceOfInitialCapital
    business_association_type: AssociationType
    customerId: str
    @field_validator("business_tin_number")
    def validate_tin(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError("Business TIN must be 10 digits")
        return v

# --- Helper Functions ---
def _random_name() -> str:
    first = np.random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) + "".join(
        np.random.choice(list("abcdefghijklmnopqrstuvwxyz"), np.random.randint(3, 8))
    )
    last = np.random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) + "".join(
        np.random.choice(list("abcdefghijklmnopqrstuvwxyz"), np.random.randint(3, 12))
    )
    return f"{first} {last}"

def _random_tin() -> str:
    return "".join(np.random.choice(list("0123456789"), 10))

def _random_phone() -> int:
    return int("9" + "".join(np.random.choice(list("0123456789"), 8)))

def _random_bank_account() -> str:
    return "".join(np.random.choice(list("0123456789"), 13))

# --- Data Generation ---
def generate_kyc_data(n_samples: int = 10000, anomaly_fraction: float = 0.02) -> pd.DataFrame:
    np.random.seed(42)
    n_normal = int(n_samples * (1 - anomaly_fraction))
    records = []
    for i in range(n_samples):
        is_anomaly = i >= n_normal
        try:
            age = int(np.clip(np.random.normal(45, 15), 18, 80))
            if is_anomaly:
                age = np.random.choice([16, 17, 85, 95])
            record = CustomerKYC(
                customer_phone_number=_random_phone(),
                customer_age=age,
                customer_gender=Gender(np.random.choice([g.value for g in Gender])),
                customer_marital_status=MaritalStatusOptions(np.random.choice([m.value for m in MaritalStatusOptions])),
                customer_education_level=EducationalLevelOptions(np.random.choice([e.value for e in EducationalLevelOptions])),
                customer_tin_number=_random_tin(),
                customer_name=_random_name() if not is_anomaly else "Suspicious Name",
                customer_bank_account_number=_random_bank_account(),
                customer_region=Region(np.random.choice([r.value for r in Region])),
                customer_city=City(np.random.choice([c.value for c in City])),
                customer_zone_or_sub_city=ZoneOrSubCity(np.random.choice([z.value for z in ZoneOrSubCity])),
                customer_woreda=str(np.random.randint(1, 16)),
                customerId=f"CUST_{i:06d}",
            ).model_dump()
            record["is_anomaly"] = int(is_anomaly)
            records.append(record)
        except Exception:
            continue
    return pd.DataFrame(records)

def generate_business_data(customer_ids: list, anomaly_fraction: float = 0.02) -> pd.DataFrame:
    np.random.seed(42)
    n_samples = len(customer_ids)
    n_normal = int(n_samples * (1 - anomaly_fraction))
    records = []
    ASSOCIATIONS = [a.value for a in AssociationType]
    SECTORS = [s.value for s in BusinessSector]
    for i, cust_id in enumerate(customer_ids):
        is_anomaly = i >= n_normal
        association = np.random.choice(ASSOCIATIONS)
        sector = np.random.choice(SECTORS)
        est_year = np.random.randint(2000, 2025)
        if is_anomaly:
            est_year = np.random.choice([1850, 2030])
            starting_cap = np.random.choice([10, 10_000_000])
        else:
            starting_cap = np.random.uniform(50_000, 500_000)
        current_cap = starting_cap * np.random.uniform(0.8, 3.0)
        annual_sales = current_cap * np.random.uniform(0.5, 2.0)
        annual_profit = annual_sales * np.random.uniform(-0.1, 0.4)
        try:
            biz = BusinessInformation(
                business_establishment_year=est_year,
                business_sector=BusinessSector(sector),
                business_level=BusinessLevel.STARTUP if est_year > 2020 else BusinessLevel.GROWING,
                business_tin_number=_random_tin(),
                business_region=Region.ADDIS_ABABA,
                business_city=City.ADDIS_ABABA,
                business_subcity=City.ADDIS_ABABA,
                business_woreda="1",
                business_zone_or_sub_city=ZoneOrSubCity.BOLE,
                business_starting_capital=float(starting_cap),
                business_current_capital=float(current_cap),
                business_annual_profit=float(annual_profit),
                business_annual_sales=float(annual_sales),
                business_starting_no_of_employees=int(np.random.randint(1, 20)),
                business_current_no_of_employees=int(np.random.randint(1, 50)),
                business_source_of_initial_capital=SourceOfInitialCapital(np.random.choice([s.value for s in SourceOfInitialCapital])),
                business_association_type=AssociationType(association),
                customerId=cust_id,
            )
            rec = biz.model_dump()
            rec["is_anomaly"] = int(is_anomaly)
            records.append(rec)
        except Exception:
            continue
    return pd.DataFrame(records)

def generate_transaction_data(customer_ids: list, anomaly_flags: list, n_days: int = 365) -> pd.DataFrame:
    np.random.seed(42)
    all_transactions = []
    start_date = pd.to_datetime("2024-10-26")
    ROUND_AMOUNTS = [100, 500, 1000, 5000, 10000, 50000]
    for cust_id, is_anomaly in zip(customer_ids, anomaly_flags):
        balance = np.random.uniform(1000, 50000)
        current_date = start_date
        for day in range(n_days):
            is_weekend = (current_date.weekday() >= 5)
            base_txns = 0 if not is_anomaly else np.random.randint(0, 3)
            extra_txns = 0
            if is_anomaly:
                if np.random.rand() < 0.3:
                    extra_txns = np.random.randint(3, 8)
                elif np.random.rand() < 0.2 and not is_weekend:
                    extra_txns = np.random.randint(1, 4)
            n_txns = base_txns + extra_txns
            for _ in range(n_txns):
                if is_anomaly and np.random.rand() < 0.4:
                    amount = float(np.random.choice([1000, 5000, 10000, 50000]))
                    if np.random.rand() < 0.5 and balance > amount:
                        balance -= amount
                        all_transactions.append({
                            "customer_id": cust_id,
                            "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "credit": 0.0,
                            "debit": amount,
                            "closingBalance": max(0, round(balance, 2)),
                            "narrative": "CASH WITHDRAW-",
                            "source": "CASH WITHDRAW",
                            "is_anomaly": 1,
                        })
                    else:
                        balance += amount
                        all_transactions.append({
                            "customer_id": cust_id,
                            "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "credit": amount,
                            "debit": 0.0,
                            "closingBalance": round(balance, 2),
                            "narrative": "ft",
                            "source": "FUND TRANSFER",
                            "is_anomaly": 1,
                        })
                else:
                    if np.random.rand() < 0.5:
                        amt = float(np.random.choice([100, 500, 1000, 5000]))
                        balance += amt
                        all_transactions.append({
                            "customer_id": cust_id,
                            "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "credit": amt,
                            "debit": 0.0,
                            "closingBalance": round(balance, 2),
                            "narrative": "Cash Deposit",
                            "source": "CASH DEPOSIT",
                            "is_anomaly": int(is_anomaly),
                        })
                    elif balance > 100:
                        amt = min(float(np.random.choice([100, 500, 1000])), balance)
                        balance -= amt
                        all_transactions.append({
                            "customer_id": cust_id,
                            "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "credit": 0.0,
                            "debit": amt,
                            "closingBalance": max(0, round(balance, 2)),
                            "narrative": "CASH WITHDRAW-",
                            "source": "CASH WITHDRAW",
                            "is_anomaly": int(is_anomaly),
                        })
            current_date += pd.Timedelta(days=1)
    return pd.DataFrame(all_transactions)

# --- Main ---
def main(n_samples=10000, anomaly_fraction=0.02, output_dir="data/raw"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Generating {n_samples} training samples with {anomaly_fraction:.1%} anomalies")
    kyc_df = generate_kyc_data(n_samples, anomaly_fraction)
    kyc_df.to_csv(output_dir / "kyc_training_data.csv", index=False)
    customer_ids = kyc_df["customerId"].tolist()
    business_df = generate_business_data(customer_ids, anomaly_fraction)
    business_df.to_csv(output_dir / "business_training_data.csv", index=False)
    merged_df = pd.merge(kyc_df, business_df, on="customerId", suffixes=("_kyc", "_biz"))
    merged_df["is_anomaly"] = ((merged_df["is_anomaly_kyc"] == 1) | (merged_df["is_anomaly_biz"] == 1)).astype(int)
    merged_df = merged_df.drop(columns=["is_anomaly_kyc", "is_anomaly_biz"])
    merged_df.to_csv(output_dir / "kyc_business_training_data.csv", index=False)
    anomaly_flags = merged_df["is_anomaly"].tolist()
    txn_df = generate_transaction_data(customer_ids, anomaly_flags, n_days=365)
    txn_df.to_csv(output_dir / "transaction_training_data.csv", index=False)
    print("✅ Training data generation complete!")

if __name__ == "__main__":
    main()
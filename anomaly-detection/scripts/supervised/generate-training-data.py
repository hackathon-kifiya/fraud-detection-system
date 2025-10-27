import os
import sys
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator

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
    NO_EDUCATION_BACKGROUND="NO_EDUCATION_BACKGROUND"


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


# ======================
# Pydantic Models with Strict Validation
# ======================


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


# ======================
# Helper Functions
# ======================


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


# ======================
# Data Generation Functions
# ======================


def generate_kyc_data(
    n_samples: int = 10000, anomaly_fraction: float = 0.1
) -> pd.DataFrame:
    np.random.seed(42)
    n_normal = int(n_samples * (1 - anomaly_fraction))
    n_anomaly = n_samples - n_normal
    print(
        f"Generating {n_samples} KYC records ({n_normal} normal, {n_anomaly} anomalies)"
    )

    normal_records = []
    for i in range(n_normal):
        try:
            record = CustomerKYC(
                customer_phone_number=_random_phone(),
                customer_age=int(np.clip(np.random.normal(45, 15), 18, 80)),
                customer_gender=Gender(np.random.choice([g.value for g in Gender])),
                customer_marital_status=MaritalStatusOptions(
                    np.random.choice(
                        [m.value for m in MaritalStatusOptions],
                        p=[0.45, 0.48, 0.05, 0.02],
                    )
                ),
                customer_education_level=EducationalLevelOptions(
                    np.random.choice([e.value for e in EducationalLevelOptions])
                ),
                customer_tin_number=_random_tin(),
                customer_name=_random_name(),
                customer_bank_account_number=_random_bank_account(),
                customer_region=Region(np.random.choice([r.value for r in Region])),
                customer_city=City(np.random.choice([c.value for c in City])),
                customer_zone_or_sub_city=ZoneOrSubCity(
                    np.random.choice([z.value for z in ZoneOrSubCity])
                ),
                customer_woreda=str(np.random.randint(1, 16)),
                customerId=f"CUST_{i:06d}",
            ).model_dump()
            record["is_anomaly"] = 0
            normal_records.append(record)
        except Exception as e:
            print(f"Warning: Skipping normal KYC record {i}: {e}")

    anomaly_records = []
    for i in range(n_normal, n_samples):
        # Age anomalies (still within 0–130, but suspicious)
        age = np.random.choice(
            [
                int(np.random.uniform(15, 17)),  # Near minor
                int(np.random.uniform(80, 100)),  # Very elderly
                int(np.clip(np.random.normal(45, 15), 18, 80)),
            ],
            p=[0.3, 0.3, 0.4],
        )

        # ALL ENUMS USE VALID VALUES ONLY
        region = Region(np.random.choice([r.value for r in Region]))
        city = City(np.random.choice([c.value for c in City]))
        zone = ZoneOrSubCity(np.random.choice([z.value for z in ZoneOrSubCity]))
        woreda = str(np.random.randint(1, 16))

        # Format-valid but suspicious TIN/account/phone
        tin_number = (
            _random_tin()
            if np.random.rand() > 0.2
            else "".join(np.random.choice(list("0123456789"), 10))
        )
        account_number = (
            _random_bank_account()
            if np.random.rand() > 0.1
            else "".join(np.random.choice(list("0123456789"), 13))
        )
        phone = (
            _random_phone()
            if np.random.rand() > 0.15
            else int("9" + "".join(np.random.choice(list("0123456789"), 8)))
        )
        name = _random_name() if np.random.rand() > 0.1 else "Anonymous Customer"

        marital_status = MaritalStatusOptions(
            np.random.choice([m.value for m in MaritalStatusOptions])
        )
        education = EducationalLevelOptions(
            np.random.choice([e.value for e in EducationalLevelOptions])
        )

        try:
            record = CustomerKYC(
                customer_phone_number=phone,
                customer_age=age,
                customer_gender=Gender(np.random.choice([g.value for g in Gender])),
                customer_marital_status=marital_status,
                customer_education_level=education,
                customer_tin_number=tin_number,
                customer_name=name,
                customer_bank_account_number=account_number,
                customer_region=region,
                customer_city=city,
                customer_zone_or_sub_city=zone,
                customer_woreda=woreda,
                customerId=f"CUST_{i:06d}",
            ).model_dump()
            record["is_anomaly"] = 1
            anomaly_records.append(record)
        except Exception as e:
            # Fallback (should rarely occur)
            rec = {
                "customer_phone_number": phone,
                "customer_age": age,
                "customer_gender": np.random.choice([g.value for g in Gender]),
                "customer_marital_status": marital_status.value,
                "customer_education_level": education.value,
                "customer_tin_number": tin_number,
                "customer_name": name,
                "customer_bank_account_number": account_number,
                "customer_region": region.value,
                "customer_city": city.value,
                "customer_zone_or_sub_city": zone.value,
                "customer_woreda": woreda,
                "customerId": f"CUST_{i:06d}",
                "is_anomaly": 1,
            }
            anomaly_records.append(rec)

    df = pd.DataFrame(normal_records + anomaly_records)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def generate_business_data(
    customer_ids: list, anomaly_fraction: float = 0.1
) -> pd.DataFrame:
    np.random.seed(42)
    n_samples = len(customer_ids)
    n_normal = int(n_samples * (1 - anomaly_fraction))
    n_anomaly = n_samples - n_normal
    print(
        f"Generating {n_samples} Business records ({n_normal} normal, {n_anomaly} anomalies)"
    )

    ASSOCIATIONS = [a.value for a in AssociationType]
    SECTORS = [s.value for s in BusinessSector]

    ASSOCIATION_PROFILES = {
        "SOLE_PROPRIETORSHIP": {
            "capital": (10_000, 500_000),
            "employees": (1, 5),
            "profit_margin": (0.05, 0.3),
            "sales_mult": (1.0, 3.0),
        },
        "PARTNERSHIP": {
            "capital": (100_000, 2_000_000),
            "employees": (2, 20),
            "profit_margin": (0.08, 0.25),
            "sales_mult": (1.5, 4.0),
        },
        "CORPORATION": {
            "capital": (500_000, 10_000_000),
            "employees": (10, 500),
            "profit_margin": (0.03, 0.2),
            "sales_mult": (2.0, 8.0),
        },
        "OTHER": {
            "capital": (5_000, 300_000),
            "employees": (1, 10),
            "profit_margin": (0.02, 0.4),
            "sales_mult": (0.5, 2.5),
        },
    }

    records = []
    for idx, cust_id in enumerate(customer_ids):
        is_anomaly = idx >= n_normal

        if not is_anomaly:
            association = np.random.choice(ASSOCIATIONS, p=[0.6, 0.25, 0.1, 0.05])
            profile = ASSOCIATION_PROFILES[association]
            starting_cap = np.random.uniform(*profile["capital"])
            start_employees = max(1, int(np.random.uniform(*profile["employees"])))
            growth = np.random.uniform(1.0, 3.0)
            current_cap = starting_cap * growth
            current_employees = int(start_employees * np.random.uniform(1.0, 4.0))
            sales_mult = np.random.uniform(*profile["sales_mult"])
            annual_sales = current_cap * sales_mult
            profit_margin = np.random.uniform(*profile["profit_margin"])
            annual_profit = annual_sales * profit_margin
            est_year = np.random.randint(1995, 2025)
            sector = np.random.choice(SECTORS, p=[0.25, 0.2, 0.4, 0.1, 0.05])
            level = BusinessLevel.STARTUP if est_year >= 2020 else BusinessLevel.GROWING
            source = np.random.choice(
                [s.value for s in SourceOfInitialCapital], p=[0.2, 0.3, 0.4, 0.05, 0.05]
            )

            try:
                biz = BusinessInformation(
                    business_establishment_year=est_year,
                    business_sector=BusinessSector(sector),
                    business_level=level,
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
                    business_starting_no_of_employees=int(start_employees),
                    business_current_no_of_employees=int(current_employees),
                    business_source_of_initial_capital=SourceOfInitialCapital(source),
                    business_association_type=AssociationType(association),
                    customerId=cust_id,
                )
                rec = biz.model_dump()
                rec["is_anomaly"] = 0
                records.append(rec)
            except Exception as e:
                print(f"Warning: Skipping normal business record for {cust_id}: {e}")
        else:
            # Anomaly: use ONLY valid enums, but illogical values
            association = np.random.choice(ASSOCIATIONS)
            sector = np.random.choice(SECTORS)
            level = np.random.choice([level.value for level in BusinessLevel])
            source = np.random.choice([s.value for s in SourceOfInitialCapital])
            region = Region(np.random.choice([r.value for r in Region]))
            city = City(np.random.choice([c.value for c in City]))
            zone = ZoneOrSubCity(np.random.choice([z.value for z in ZoneOrSubCity]))
            woreda = str(np.random.randint(1, 16))

            # Logical anomalies
            if np.random.rand() < 0.7:
                if association == "SOLE_PROPRIETORSHIP":
                    starting_cap = np.random.uniform(
                        5_000_000, 50_000_000
                    )  # Extremely high
                    start_employees = np.random.randint(100, 1000)  # Implausible
                elif association == "CORPORATION":
                    starting_cap = np.random.uniform(100, 10_000)  # Suspiciously low
                    start_employees = 0  # No staff?
                else:
                    starting_cap = np.random.choice([0, 1, 10])  # Near-zero
                    start_employees = np.random.choice([0, 1])
            else:
                base_assoc = np.random.choice(ASSOCIATIONS)
                profile = ASSOCIATION_PROFILES[base_assoc]
                starting_cap = np.random.uniform(
                    profile["capital"][0] * 0.01, profile["capital"][1] * 20
                )
                start_employees = int(
                    np.random.uniform(0, profile["employees"][1] * 10)
                )

            # Financial anomalies
            if np.random.rand() < 0.4:
                current_cap = -abs(starting_cap) * np.random.uniform(
                    0.01, 0.1
                )  # Small negative (data glitch)
                annual_sales = np.random.uniform(1000, 100000)
                annual_profit = -np.random.uniform(100, 50000)
            else:
                current_cap = starting_cap * np.random.uniform(0.1, 5)
                annual_sales = current_cap * np.random.uniform(0.1, 3)
                if np.random.rand() < 0.3:
                    annual_profit = annual_sales * np.random.uniform(
                        1.01, 2.0
                    )  # Profit > sales
                else:
                    annual_profit = annual_sales * np.random.uniform(
                        -0.2, 0.5
                    )  # Loss or low profit

            current_employees = int(start_employees * np.random.uniform(0, 5))
            est_year = np.random.choice(
                [
                    np.random.randint(1800, 1900),
                    np.random.randint(2026, 2030),
                    np.random.randint(1990, 2025),
                ],
                p=[0.2, 0.2, 0.6],
            )

            tin = _random_tin()

            try:
                biz = BusinessInformation(
                    business_establishment_year=est_year,
                    business_sector=BusinessSector(sector),
                    business_level=BusinessLevel(level),
                    business_tin_number=tin,
                    business_region=region,
                    business_city=city,
                    business_subcity=city,
                    business_woreda=woreda,
                    business_zone_or_sub_city=zone,
                    business_starting_capital=float(starting_cap),
                    business_current_capital=float(current_cap),
                    business_annual_profit=float(annual_profit),
                    business_annual_sales=float(annual_sales),
                    business_starting_no_of_employees=int(start_employees),
                    business_current_no_of_employees=int(current_employees),
                    business_source_of_initial_capital=SourceOfInitialCapital(source),
                    business_association_type=AssociationType(association),
                    customerId=cust_id,
                )
                rec = biz.model_dump()
                rec["is_anomaly"] = 1
                records.append(rec)
            except Exception as e:
                rec = {
                    "business_establishment_year": est_year,
                    "business_sector": sector,
                    "business_level": level,
                    "business_tin_number": tin,
                    "business_region": region.value,
                    "business_city": city.value,
                    "business_subcity": city.value,
                    "business_woreda": woreda,
                    "business_zone_or_sub_city": zone.value,
                    "business_starting_capital": float(starting_cap),
                    "business_current_capital": float(current_cap),
                    "business_annual_profit": float(annual_profit),
                    "business_annual_sales": float(annual_sales),
                    "business_starting_no_of_employees": int(start_employees),
                    "business_current_no_of_employees": int(current_employees),
                    "business_source_of_initial_capital": source,
                    "business_association_type": association,
                    "customerId": cust_id,
                    "is_anomaly": 1,
                }
                records.append(rec)

    return pd.DataFrame(records)


def generate_transaction_data(
    customer_ids: list, anomaly_flags: list, n_days: int = 365
) -> pd.DataFrame:
    np.random.seed(42)
    all_transactions = []
    start_date = pd.to_datetime("2024-10-26")
    ROUND_AMOUNTS = [50, 100, 500, 1000, 5000, 10000, 20000, 35000, 50000, 110000]

    for cust_id, is_anomaly in zip(customer_ids, anomaly_flags):
        balance = 0.0
        transactions = []

        # Opening deposit
        if np.random.rand() > 0.3:
            open_amt = 50.0
            balance += open_amt
            transactions.append(
                {
                    "customer_id": cust_id,
                    "date": start_date.strftime("%Y-%m-%dT00:00"),
                    "credit": open_amt,
                    "debit": 0.0,
                    "closingBalance": balance,
                    "narrative": "Cash Deposit BY SELF",
                    "source": "CASH DEPOSIT",
                    "is_anomaly": int(is_anomaly),
                }
            )

        current_date = start_date
        for _ in range(n_days):
            is_active = np.random.rand() < (0.7 if is_anomaly else 0.08)
            n_txns = (
                np.random.randint(4, 21)
                if (is_anomaly and is_active)
                else (np.random.randint(1, 6) if is_active else 0)
            )

            day_txns = []
            for _ in range(n_txns):
                if is_anomaly and np.random.rand() < 0.5:
                    amount = float(np.random.choice(ROUND_AMOUNTS))
                    if np.random.rand() < 0.5 and balance >= amount:
                        balance -= amount
                        day_txns.append(
                            {
                                "customer_id": cust_id,
                                "date": current_date.strftime("%Y-%m-%dT00:00"),
                                "credit": 0.0,
                                "debit": amount,
                                "closingBalance": max(0, round(balance, 2)),
                                "narrative": "CASH WITHDRAW-",
                                "source": "CASH WITHDRAW",
                                "is_anomaly": 1,
                            }
                        )
                    else:
                        balance += amount
                        day_txns.append(
                            {
                                "customer_id": cust_id,
                                "date": current_date.strftime("%Y-%m-%dT00:00"),
                                "credit": amount,
                                "debit": 0.0,
                                "closingBalance": round(balance, 2),
                                "narrative": "ft",
                                "source": "FUND TRANSFER",
                                "is_anomaly": 1,
                            }
                        )
                else:
                    source = np.random.choice(
                        [
                            "CASH DEPOSIT",
                            "FUND TRANSFER",
                            "CASH WITHDRAW",
                            "TELE BIRR INCOMING",
                        ],
                        p=[0.3, 0.3, 0.3, 0.1],
                    )
                    if source in ["CASH DEPOSIT", "TELE BIRR INCOMING"]:
                        p_raw = [0.15, 0.12, 0.08, 0.1, 0.05, 0.12, 0.1, 0.08, 0.06, 0.04]
                        p = np.array(p_raw)
                        p = p / p.sum()
                        amount = np.random.choice(ROUND_AMOUNTS, p=p)
                        balance += amount
                        day_txns.append(
                            {
                                "customer_id": cust_id,
                                "date": current_date.strftime("%Y-%m-%dT00:00"),
                                "credit": float(amount),
                                "debit": 0.0,
                                "closingBalance": round(balance, 2),
                                "narrative": "Cash Deposit"
                                if source == "CASH DEPOSIT"
                                else "null",
                                "source": source,
                                "is_anomaly": int(is_anomaly),
                            }
                        )
                    elif balance > 0:
                        amount = min(
                            np.random.choice([50, 100, 500, 1000, 5000]), balance
                        )
                        balance -= amount
                        day_txns.append(
                            {
                                "customer_id": cust_id,
                                "date": current_date.strftime("%Y-%m-%dT00:00"),
                                "credit": 0.0,
                                "debit": float(amount),
                                "closingBalance": max(0, round(balance, 2)),
                                "narrative": "CASH WITHDRAW-",
                                "source": "CASH WITHDRAW",
                                "is_anomaly": int(is_anomaly),
                            }
                        )

            transactions.extend(day_txns)
            current_date += pd.Timedelta(days=1)

        all_transactions.extend(transactions)

    return pd.DataFrame(all_transactions)


# ======================
# Main Execution - Google Colab Version
# ======================


def main(n_samples=10000, anomaly_fraction=0.1, output_dir="data/raw"):
    """
    Generate synthetic training data

    Parameters:
    -----------
    n_samples : int
        Number of customer samples (default: 10000)
    anomaly_fraction : float
        Fraction of anomalous records between 0.0 and 1.0 (default: 0.1)
    output_dir : str
        Output directory for CSV files (default: "data/raw")
    """

    if not (0.0 <= anomaly_fraction <= 1.0):
        raise ValueError("anomaly_fraction must be between 0.0 and 1.0")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("GENERATING SYNTHETIC TRAINING DATA")
    print("All anomalies are logical — no invalid enum values.")
    print("=" * 60)

    # Generate KYC
    kyc_df = generate_kyc_data(n_samples, anomaly_fraction)
    kyc_path = output_dir / "kyc_training_data.csv"
    kyc_df.to_csv(kyc_path, index=False)
    print(f"✓ KYC data saved to: {kyc_path}")

    # Generate Business (aligned)
    customer_ids = kyc_df["customerId"].tolist()
    business_df = generate_business_data(customer_ids, anomaly_fraction)
    business_path = output_dir / "business_training_data.csv"
    business_df.to_csv(business_path, index=False)
    print(f"✓ Business data saved to: {business_path}")

    # Merge KYC + Business
    merged_df = pd.merge(
        kyc_df, business_df, on="customerId", suffixes=("_kyc", "_biz")
    )
    merged_df["is_anomaly"] = (
        (merged_df["is_anomaly_kyc"] == 1) | (merged_df["is_anomaly_biz"] == 1)
    ).astype(int)
    merged_df = merged_df.drop(columns=["is_anomaly_kyc", "is_anomaly_biz"])
    merged_path = output_dir / "kyc_business_training_data.csv"
    merged_df.to_csv(merged_path, index=False)
    print(f"✓ Merged data saved to: {merged_path} (shape: {merged_df.shape})")

    # Generate Transactions
    anomaly_flags = merged_df["is_anomaly"].tolist()
    txn_df = generate_transaction_data(customer_ids, anomaly_flags)
    txn_path = output_dir / "transaction_training_data.csv"
    txn_df.to_csv(txn_path, index=False)
    print(f"✓ Transaction data saved to: {txn_path} (shape: {txn_df.shape})")

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    # Configure these parameters as needed
    N_SAMPLES = 10000          # Number of customer samples
    ANOMALY_FRACTION = 0.1     # 10% anomalies
    OUTPUT_DIR = "data/raw"    # Output directory

    main(n_samples=N_SAMPLES,
         anomaly_fraction=ANOMALY_FRACTION,
         output_dir=OUTPUT_DIR)
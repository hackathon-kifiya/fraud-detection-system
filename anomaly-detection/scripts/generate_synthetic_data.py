"""
Generate Synthetic Training Data
Creates realistic synthetic data for training anomaly detection models
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse  # noqa: E402
from pathlib import Path  # noqa: E402
from enum import Enum  # noqa: E402
from pydantic import BaseModel  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# ======================
# Enums
# ======================

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

class MaritalStatusOptions(Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class EducationalLevelOptions(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    POST_GRADUATE = "post_graduate"

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
# Pydantic Models
# ======================

class CustomerKYC(BaseModel):
    customer_phone_number: int
    customer_age: int
    customer_gender: Gender
    customer_marital_status: MaritalStatusOptions
    customer_education_level: EducationalLevelOptions
    customer_tin_number: str
    customer_name: str
    customer_bank_account_number: str
    customer_region: str
    customer_city: str
    customer_zone_or_sub_city: str
    customer_woreda: str
    customerId: str

class BusinessInformation(BaseModel):
    business_establishment_year: int
    business_sector: str
    business_level: str
    business_tin_number: str
    business_city: str
    business_subcity: str
    business_region: str
    business_woreda: str
    business_zone_or_sub_city: str
    business_starting_capital: float
    business_current_capital: float
    business_annual_profit: float
    business_annual_sales: float
    business_current_no_of_employees: int
    business_starting_no_of_employees: int
    business_source_of_initial_capital: str
    business_association_type: str
    customerId: str

# ======================
# Data Generation Functions
# ======================

def generate_kyc_data(n_samples: int = 10000, anomaly_fraction: float = 0.1):
    np.random.seed(42)
    n_normal = int(n_samples * (1 - anomaly_fraction))
    n_anomaly = n_samples - n_normal
    print(f"Generating {n_samples} KYC records ({n_normal} normal, {n_anomaly} anomalies)")

    GENDERS = [g.value for g in Gender]
    MARITAL_STATUSES = [m.value for m in MaritalStatusOptions]
    EDU_LEVELS = [e.value for e in EducationalLevelOptions]
    REGIONS = [r.value for r in Region]
    CITIES = [c.value for c in City]
    ZONES = [z.value for z in ZoneOrSubCity]

    def random_name():
        first = ''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 1)) + \
                ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), np.random.randint(3, 8)))
        last = ''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 1)) + \
                ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), np.random.randint(3, 12)))
        return f"{first} {last}"

    def random_tin():
        return ''.join(np.random.choice(list('0123456789'), 10))

    def random_phone():
        return int("9" + ''.join(np.random.choice(list('0123456789'), 8)))

    def random_bank_account():
        return ''.join(np.random.choice(list('0123456789'), 13))

    normal_records = []
    for i in range(n_normal):
        norm = CustomerKYC(
            customer_phone_number=random_phone(),
            customer_age=int(np.clip(np.random.normal(45, 15), 18, 80)),
            customer_gender=Gender(np.random.choice(GENDERS)),
            customer_marital_status=MaritalStatusOptions(np.random.choice(MARITAL_STATUSES, p=[0.45, 0.48, 0.05, 0.02])),
            customer_education_level=EducationalLevelOptions(np.random.choice(EDU_LEVELS, p=[0.2, 0.45, 0.3, 0.05])),
            customer_tin_number=random_tin(),
            customer_name=random_name(),
            customer_bank_account_number=random_bank_account(),
            customer_region=np.random.choice(REGIONS),
            customer_city=np.random.choice(CITIES),
            customer_zone_or_sub_city=np.random.choice(ZONES),
            customer_woreda=str(np.random.randint(1, 16)),
            customerId=f"CUST_{i:06d}"
        )
        rec = norm.dict()
        rec['is_anomaly'] = 0
        normal_records.append(rec)

    anomaly_records = []
    for i in range(n_normal, n_samples):
        age_group = np.random.choice(['young', 'old', 'normal'])
        if age_group == 'young':
            age = int(np.random.uniform(10, 16))
        elif age_group == 'old':
            age = int(np.random.uniform(90, 120))
        else:
            age = int(np.clip(np.random.normal(45, 15), 18, 80))

        education = np.random.choice(EDU_LEVELS + [None], p=[0.1, 0.15, 0.2, 0.05, 0.5])
        marital_status = np.random.choice(MARITAL_STATUSES + [None], p=[0.2, 0.25, 0.05, 0.05, 0.45])
        region = np.random.choice(REGIONS + ["UNKNOWN"])
        city = np.random.choice(CITIES + ["UNKNOWN"])
        zone = np.random.choice(ZONES + ["UNKNOWN"])
        woreda = str(np.random.choice(["-1", "0", "1000"]))
        tin_number = random_tin() if np.random.rand() > 0.2 else ''.join(np.random.choice(list('ABCDEFGHIJ'), 10))
        account_number = random_bank_account() if np.random.rand() > 0.1 else ''.join(np.random.choice(list('abcdXYZ'), 10))
        phone = random_phone() if np.random.rand() > 0.15 else int(np.random.choice([1111, 9999, 123]))
        name = random_name() if np.random.rand() > 0.1 else "Anonymous"

        try:
            rec = CustomerKYC(
                customer_phone_number=phone,
                customer_age=age,
                customer_gender=Gender(np.random.choice(GENDERS)),
                customer_marital_status=MaritalStatusOptions(marital_status) if marital_status else MaritalStatusOptions.SINGLE,
                customer_education_level=EducationalLevelOptions(education) if education else EducationalLevelOptions.PRIMARY,
                customer_tin_number=tin_number,
                customer_name=name,
                customer_bank_account_number=account_number,
                customer_region=region,
                customer_city=city,
                customer_zone_or_sub_city=zone,
                customer_woreda=woreda,
                customerId=f"CUST_{i:06d}"
            ).dict()
        except Exception:
            rec = dict(
                customer_phone_number=phone,
                customer_age=age,
                customer_gender=np.random.choice(GENDERS),
                customer_marital_status=marital_status if marital_status else "single",
                customer_education_level=education if education else "primary",
                customer_tin_number=tin_number,
                customer_name=name,
                customer_bank_account_number=account_number,
                customer_region=region,
                customer_city=city,
                customer_zone_or_sub_city=zone,
                customer_woreda=woreda,
                customerId=f"CUST_{i:06d}"
            )
        rec['is_anomaly'] = 1
        anomaly_records.append(rec)

    df = pd.DataFrame(normal_records + anomaly_records)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def generate_business_data(n_samples: int = 10000, anomaly_fraction: float = 0.1, kyc_df: pd.DataFrame = None):
    np.random.seed(42)
    n_normal = int(n_samples * (1 - anomaly_fraction))
    n_anomaly = n_samples - n_normal
    print(f"Generating {n_samples} Business records ({n_normal} normal, {n_anomaly} anomalies)")

    ASSOCIATIONS = [a.value for a in AssociationType]
    SECTORS = [s.value for s in BusinessSector]

    # Realistic profiles by association type
    ASSOCIATION_PROFILES = {
        "SOLE_PROPRIETORSHIP": {
            "capital_range": (10_000, 500_000),
            "employee_range": (1, 5),
            "profit_margin": (0.05, 0.3),
            "sales_multiplier": (1.0, 3.0)  # sales = capital * multiplier
        },
        "PARTNERSHIP": {
            "capital_range": (100_000, 2_000_000),
            "employee_range": (2, 20),
            "profit_margin": (0.08, 0.25),
            "sales_multiplier": (1.5, 4.0)
        },
        "CORPORATION": {
            "capital_range": (500_000, 10_000_000),
            "employee_range": (10, 500),
            "profit_margin": (0.03, 0.2),  
            "sales_multiplier": (2.0, 8.0)
        },
        "OTHER": {
            "capital_range": (5_000, 300_000),
            "employee_range": (1, 10),
            "profit_margin": (0.02, 0.4),
            "sales_multiplier": (0.5, 2.5)
        }
    }

    business_records = []

    for i in range(n_samples):
        is_anomaly = i >= n_normal

        if not is_anomaly:
            # Normal: pick association type with realistic weights
            association = np.random.choice(
                ASSOCIATIONS,
                p=[0.6, 0.25, 0.1, 0.05]  # SOLE > PARTNERSHIP > CORP > OTHER
            )
            profile = ASSOCIATION_PROFILES[association]

            # Sample capital and employees within profile
            starting_cap = np.random.uniform(*profile["capital_range"])
            start_employees = int(np.random.uniform(*profile["employee_range"]))

            # Ensure employees ≥ 1
            start_employees = max(1, start_employees)

            # Growth over time
            growth_factor = np.random.uniform(1.0, 3.0)
            current_cap = starting_cap * growth_factor
            current_employees = int(start_employees * np.random.uniform(1.0, 4.0))

            # Sales & profit derived from capital
            sales_mult = np.random.uniform(*profile["sales_multiplier"])
            annual_sales = current_cap * sales_mult
            profit_margin = np.random.uniform(*profile["profit_margin"])
            annual_profit = annual_sales * profit_margin

            # Other fields
            est_year = np.random.randint(1995, 2025)
            sector = np.random.choice(SECTORS, p=[0.25, 0.2, 0.4, 0.1, 0.05])
            level = BusinessLevel.STARTUP if est_year >= 2020 else BusinessLevel.GROWING
            source = np.random.choice([s.value for s in SourceOfInitialCapital], p=[0.2, 0.3, 0.4, 0.05, 0.05])

            # Use KYC location if available (optional)
            region = city = zone = woreda = "ADDIS_ABABA"  # Simplified; you can re-add if needed

        else:
            # Anomalous: break correlations
            association = np.random.choice(ASSOCIATIONS + ["FAKE"], p=[0.15, 0.1, 0.05, 0.1, 0.6])

            # Inject illogical capital/employee combos
            if np.random.rand() < 0.7:
                # Extreme mismatch
                if association == "SOLE_PROPRIETORSHIP":
                    starting_cap = np.random.uniform(1_000_000, 20_000_000)  # 1M–20M
                    start_employees = np.random.randint(50, 500)
                elif association == "CORPORATION":
                    starting_cap = np.random.uniform(100, 5_000)  # Tiny capital
                    start_employees = 0  # No employees
                else:
                    # Random absurd values
                    starting_cap = np.random.choice([-50000, 0, 1, 999999999])
                    start_employees = np.random.choice([-5, 0, 1000])
            else:
                # Sample from profile but add noise
                base_assoc = np.random.choice(ASSOCIATIONS)
                profile = ASSOCIATION_PROFILES[base_assoc]
                starting_cap = np.random.uniform(profile["capital_range"][0] * 0.1, profile["capital_range"][1] * 10)
                start_employees = int(np.random.uniform(0, profile["employee_range"][1] * 5))

            # Illogical financials
            if np.random.rand() < 0.4:
                current_cap = -abs(starting_cap) * np.random.uniform(0.5, 2)
                annual_sales = -np.random.uniform(1000, 100000)
                annual_profit = -np.random.uniform(100, 50000)
            else:
                current_cap = starting_cap * np.random.uniform(0.1, 5)
                annual_sales = current_cap * np.random.uniform(0.1, 3)
                # Profit > sales? Impossible!
                if np.random.rand() < 0.2:
                    annual_profit = annual_sales * np.random.uniform(1.1, 3.0)  # >100% margin
                else:
                    annual_profit = annual_sales * np.random.uniform(-0.5, 0.5)

            current_employees = int(start_employees * np.random.uniform(0, 3))
            est_year = np.random.choice([
                np.random.randint(1800, 1950),
                np.random.randint(2026, 2035),
                np.random.randint(1990, 2025)
            ], p=[0.3, 0.3, 0.4])
            sector = np.random.choice(SECTORS + ["UNKNOWN"], p=[0.15, 0.1, 0.2, 0.05, 0.05, 0.45])
            level = np.random.choice([l.value for l in BusinessLevel] + ["INVALID"], p=[0.4, 0.4, 0.2])
            source = np.random.choice([s.value for s in SourceOfInitialCapital] + ["ILLEGAL"], p=[0.1, 0.1, 0.1, 0.05, 0.05, 0.6])
            region = city = zone = woreda = "UNKNOWN"

        # Generate TIN
        tin = ''.join(np.random.choice(list('0123456789'), 10)) if (not is_anomaly or np.random.rand() > 0.2) else ''.join(np.random.choice(list('XYZ!@#'), 10))

        try:
            business = BusinessInformation(
                business_establishment_year=est_year,
                business_sector=sector,
                business_level=level,
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
                business_source_of_initial_capital=source,
                business_association_type=association,
                customerId=f"CUST_{i:06d}"
            )
            rec = business.dict()
        except Exception:
            rec = {
                'business_establishment_year': est_year,
                'business_sector': sector,
                'business_level': level,
                'business_tin_number': tin,
                'business_region': region,
                'business_city': city,
                'business_subcity': city,
                'business_woreda': woreda,
                'business_zone_or_sub_city': zone,
                'business_starting_capital': float(starting_cap),
                'business_current_capital': float(current_cap),
                'business_annual_profit': float(annual_profit),
                'business_annual_sales': float(annual_sales),
                'business_starting_no_of_employees': int(start_employees),
                'business_current_no_of_employees': int(current_employees),
                'business_source_of_initial_capital': source,
                'business_association_type': association,
                'customerId': f"CUST_{i:06d}"
            }

        rec['is_anomaly'] = int(is_anomaly)
        business_records.append(rec)

    return pd.DataFrame(business_records)


def generate_account_transactions(customer_id: str, is_anomaly: bool = False):
    transactions = []
    balance = 0.0
    start_date = pd.to_datetime('2024-10-25')
    end_date = pd.to_datetime('2025-10-25')
    current_date = start_date

    use_only_round_amounts = is_anomaly and np.random.rand() < 0.7
    repeat_same_narrative = is_anomaly and np.random.rand() < 0.6
    high_frequency_mode = is_anomaly and np.random.rand() < 0.8
    use_fixed_amount_pattern = is_anomaly and np.random.rand() < 0.5

    ROUND_AMOUNTS = [50, 100, 500, 1000, 5000, 10000, 20000, 35000, 50000, 110000]
    FIXED_AMOUNT = float(np.random.choice([500.0, 1000.0, 5000.0, 10000.0])) if use_fixed_amount_pattern else None
    fixed_narr = np.random.choice(['initial deposit', 'ft', 'pay', 'CASH WITHDRAW-', 'null']) if repeat_same_narrative else None

    if np.random.rand() > 0.3:
        open_amt = 50.0
        balance += open_amt
        transactions.append({
            'customer_id': customer_id,
            'date': current_date.strftime('%Y-%m-%dT00:00'),
            'credit': open_amt,
            'debit': 0.0,
            'closingBalance': balance,
            'narrative': 'Cash Deposit BY SELF',
            'source': 'CASH DEPOSIT',
            'is_anomaly': int(is_anomaly)
        })

    while current_date <= end_date:
        is_active_day = (np.random.rand() < (0.7 if high_frequency_mode else 0.08))
        n_txns = np.random.randint(4, 21) if (is_anomaly and high_frequency_mode and is_active_day) else (np.random.randint(1, 6) if is_active_day else 0)

        day_transactions = []
        for _ in range(n_txns):
            if use_fixed_amount_pattern and FIXED_AMOUNT is not None:
                total_txns = len([t for t in transactions if t['customer_id'] == customer_id])
                is_incoming = (total_txns % 2 == 0)
                if is_incoming:
                    source = np.random.choice(['CASH DEPOSIT', 'FUND TRANSFER', 'TELE BIRR INCOMING'])
                    credit, debit = FIXED_AMOUNT, 0.0
                    balance += credit
                else:
                    if balance < FIXED_AMOUNT:
                        top_up = max(0, FIXED_AMOUNT - balance)
                        if top_up > 0:
                            transactions.append({
                                'customer_id': customer_id,
                                'date': current_date.strftime('%Y-%m-%dT00:00'),
                                'credit': top_up,
                                'debit': 0.0,
                                'closingBalance': balance + top_up,
                                'narrative': 'Cash Deposit',
                                'source': 'CASH DEPOSIT',
                                'is_anomaly': int(is_anomaly)
                            })
                            balance += top_up
                    if balance >= FIXED_AMOUNT:
                        source = np.random.choice(['CASH WITHDRAW', 'FUND TRANSFER'])
                        credit, debit = 0.0, FIXED_AMOUNT
                        balance -= debit
                    else:
                        continue
                narrative = fixed_narr or np.random.choice(['ft', 'initial deposit', 'null'])
                day_transactions.append({
                    'customer_id': customer_id,
                    'date': current_date.strftime('%Y-%m-%dT00:00'),
                    'credit': credit,
                    'debit': debit,
                    'closingBalance': max(0, round(balance, 2)),
                    'narrative': narrative,
                    'source': source,
                    'is_anomaly': int(is_anomaly)
                })
            else:
                if is_anomaly:
                    source = np.random.choice(['CASH DEPOSIT', 'FUND TRANSFER', 'CASH WITHDRAW', 'TELE BIRR INCOMING'], p=[0.25, 0.4, 0.3, 0.05])
                else:
                    source = np.random.choice(['CASH DEPOSIT', 'FUND TRANSFER', 'CASH WITHDRAW', 'TELE BIRR INCOMING', 'TELE BIRR OUT GOING', 'ATM card subscription fee'],
                                              p=[0.25, 0.35, 0.25, 0.1, 0.03, 0.02])

                credit = debit = 0.0
                if source in ['CASH DEPOSIT', 'TELE BIRR INCOMING']:
                    amount = float(np.random.choice(ROUND_AMOUNTS)) if use_only_round_amounts else np.random.choice(
                        [50, 100, 150, 500, 700, 1000, 5000, 10000, 20000, 35000, 50000, 110000],
                        p=[0.15, 0.12, 0.08, 0.1, 0.05, 0.12, 0.1, 0.08, 0.06, 0.05, 0.05, 0.04]
                    )
                    credit = float(amount)
                    balance += credit
                elif source in ['CASH WITHDRAW', 'TELE BIRR OUT GOING', 'FUND TRANSFER']:
                    if balance <= 0: continue
                    if use_only_round_amounts:
                        opts = [a for a in ROUND_AMOUNTS if a <= balance]
                        if not opts: continue
                        amount = float(np.random.choice(opts))
                    else:
                        ratio = np.random.choice([1.0, 0.95, 0.8, 0.5], p=[0.5, 0.2, 0.2, 0.1]) if source == 'CASH WITHDRAW' else 1.0
                        amount = min(balance * ratio, balance) if source == 'CASH WITHDRAW' else min(np.random.choice([50, 100, 500, 1000, 5000, 10000, 20000, 35000, 50000]), balance)
                        amount = round(float(amount), 2)
                    debit = amount
                    balance -= debit
                elif source == 'ATM card subscription fee':
                    if balance >= 50:
                        debit = 50.0
                        balance -= debit
                    else:
                        continue

                if credit == 0 and debit == 0:
                    continue

                narrative = fixed_narr or {
                    'CASH DEPOSIT': np.random.choice(['Cash Deposit BY SELF', 'Cash Deposit', 'NAIF KEMAL', 'null']),
                    'FUND TRANSFER': np.random.choice(['ft', 'initial deposit', 'pay', 'initial depodit']),
                    'CASH WITHDRAW': 'CASH WITHDRAW-',
                    'TELE BIRR INCOMING': 'null',
                    'TELE BIRR OUT GOING': 'ft',
                    'ATM card subscription fee': 'ATM card subscription fee'
                }.get(source, 'null')

                day_transactions.append({
                    'customer_id': customer_id,
                    'date': current_date.strftime('%Y-%m-%dT00:00'),
                    'credit': credit,
                    'debit': debit,
                    'closingBalance': max(0, round(balance, 2)),
                    'narrative': narrative,
                    'source': source,
                    'is_anomaly': int(is_anomaly)
                })

        np.random.shuffle(day_transactions)
        transactions.extend(day_transactions)
        current_date += pd.Timedelta(days=1)

    return transactions


def generate_transaction_data(n_accounts: int = 5000, anomaly_fraction: float = 0.1):
    np.random.seed(42)
    n_normal = int(n_accounts * (1 - anomaly_fraction))
    n_anomaly = n_accounts - n_normal
    all_transactions = []

    print(f"Generating transactions for {n_accounts} accounts ({n_normal} normal, {n_anomaly} anomalous)")

    for i in range(n_normal):
        print(f"Generating normal transaction for account {i}")
        cust_id = f"CUST_{i:06d}"
        all_transactions.extend(generate_account_transactions(cust_id, is_anomaly=False))

    for i in range(n_normal, n_accounts):
        cust_id = f"CUST_{i:06d}"
        all_transactions.extend(generate_account_transactions(cust_id, is_anomaly=True))

    df = pd.DataFrame(all_transactions)
    if df.empty:
        raise ValueError("No transactions generated.")
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


# ======================
# Main
# ======================

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic training data')
    parser.add_argument('--kyc-samples', type=int, default=10000, help='Number of KYC samples')
    parser.add_argument('--transaction-samples', type=int, default=10000, help='Number of transaction samples')
    parser.add_argument('--anomaly-fraction', type=float, default=0.1, help='Fraction of anomalies')
    parser.add_argument('--output-dir', type=str, default='data/raw', help='Output directory')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("GENERATING SYNTHETIC TRAINING DATA")
    print("=" * 60)

    # Generate and save KYC
    print("\n[1/3] Generating KYC data...")
    kyc_df = generate_kyc_data(args.kyc_samples, args.anomaly_fraction)
    kyc_path = output_dir / 'kyc_training_data.csv'
    kyc_df.to_csv(kyc_path, index=False)
    print(f"✓ Saved KYC data to: {kyc_path}")

    # Generate and save Business (aligned)
    print("\n[2/3] Generating Business data...")
    business_df = generate_business_data(args.kyc_samples, args.anomaly_fraction, kyc_df)
    business_path = output_dir / 'business_training_data.csv'
    business_df.to_csv(business_path, index=False)
    print(f"✓ Saved Business data to: {business_path}")

    # Merge KYC + Business
    print("\n[3/3] Merging KYC and Business data...")
    merged_df = pd.merge(kyc_df, business_df, on='customerId', suffixes=('_kyc', '_biz'))
    merged_df['is_anomaly'] = ((merged_df['is_anomaly_kyc'] == 1) | (merged_df['is_anomaly_biz'] == 1)).astype(int)
    merged_df = merged_df.drop(columns=['is_anomaly_kyc', 'is_anomaly_biz'])
    merged_path = output_dir / 'kyc_business_training_data.csv'
    merged_df.to_csv(merged_path, index=False)
    print(f"✓ Saved merged data to: {merged_path}")
    print(f"  Shape: {merged_df.shape}")
    print(f"  Anomalies: {merged_df['is_anomaly'].sum()} ({merged_df['is_anomaly'].mean() * 100:.1f}%)")

    # Generate Transaction data
    print("\n[4/4] Generating transaction data...")
    txn_df = generate_transaction_data(args.transaction_samples, args.anomaly_fraction)
    txn_path = output_dir / 'transaction_training_data.csv'
    txn_df.to_csv(txn_path, index=False)
    print(f"✓ Saved transaction data to: {txn_path}")
    print(f"  Shape: {txn_df.shape}")
    print(f"  Anomalies: {txn_df['is_anomaly'].sum()} ({txn_df['is_anomaly'].mean() * 100:.1f}%)")

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
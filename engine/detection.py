import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDetector:
    """Main fraud detection engine with statistical analysis and rule-based checks"""
    
    def __init__(self, config):
        self.config = config
        self.conn = None
    
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def get_data_for_detection(self, days_back: int = 30) -> Dict[str, pd.DataFrame]:
        """Fetch all data needed for fraud detection"""
        if not self.conn:
            self.connect_db()
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        queries = {
            'transactions': """
                SELECT txn_id, user_id, amount, timestamp, type, payment_method, 
                       items, account_balance
                FROM transactions 
                WHERE timestamp >= %s
                ORDER BY timestamp
            """,
            'loan_requests': """
                SELECT loan_id, user_id, amount_requested, purpose, request_timestamp
                FROM loan_requests 
                ORDER BY request_timestamp
            """,
            'credit_history': """
                SELECT user_id, credit_score, past_loans, defaults_count
                FROM credit_history
            """,
            'kyc': """
                SELECT user_id, verified_status, documents, verification_timestamp
                FROM kyc
            """,
            'repayments': """
                SELECT repayment_id, user_id, loan_id, amount, timestamp, status
                FROM repayments 
                ORDER BY timestamp
            """
        }
        
        data = {}
        for table, query in queries.items():
            try:
                if table == 'transactions':
                    df = pd.read_sql(query, self.conn, params=[cutoff_date])
                else:
                    df = pd.read_sql(query, self.conn)
                
                # Convert timestamp columns
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                if 'request_timestamp' in df.columns:
                    df['request_timestamp'] = pd.to_datetime(df['request_timestamp'], errors='coerce')
                if 'verification_timestamp' in df.columns:
                    df['verification_timestamp'] = pd.to_datetime(df['verification_timestamp'], errors='coerce')
                
                # Convert boolean columns
                if 'verified_status' in df.columns:
                    df['verified_status'] = df['verified_status'].astype(bool)
                
                # Convert numeric columns
                numeric_cols = ['amount', 'account_balance', 'amount_requested', 'credit_score', 'defaults_count']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                data[table] = df
                logger.info(f"Loaded {len(df)} records from {table}")
            except Exception as e:
                logger.error(f"Error loading {table}: {e}")
                data[table] = pd.DataFrame()
        
        return data
    
    def calculate_user_baselines(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Calculate baseline statistics for each user"""
        baselines = {}
        
        # Transaction baselines
        if not data['transactions'].empty:
            tx_baselines = data['transactions'].groupby('user_id').agg({
                'amount': ['mean', 'std', 'count'],
                'account_balance': 'mean'
            }).round(2)
            
            for user_id in tx_baselines.index:
                baselines[user_id] = {
                    'avg_transaction_amount': tx_baselines.loc[user_id, ('amount', 'mean')],
                    'std_transaction_amount': tx_baselines.loc[user_id, ('amount', 'std')],
                    'transaction_count': tx_baselines.loc[user_id, ('amount', 'count')],
                    'avg_account_balance': tx_baselines.loc[user_id, ('account_balance', 'mean')]
                }
        
        # Loan request baselines
        if not data['loan_requests'].empty:
            loan_baselines = data['loan_requests'].groupby('user_id').agg({
                'amount_requested': ['mean', 'count']
            }).round(2)
            
            for user_id in loan_baselines.index:
                if user_id not in baselines:
                    baselines[user_id] = {}
                baselines[user_id].update({
                    'avg_loan_amount': loan_baselines.loc[user_id, ('amount_requested', 'mean')],
                    'loan_request_count': loan_baselines.loc[user_id, ('amount_requested', 'count')]
                })
        
        # Repayment baselines
        if not data['repayments'].empty:
            repay_baselines = data['repayments'].groupby('user_id').agg({
                'amount': ['mean', 'count'],
                'status': lambda x: (x == 'late').sum()
            }).round(2)
            
            for user_id in repay_baselines.index:
                if user_id not in baselines:
                    baselines[user_id] = {}
                baselines[user_id].update({
                    'avg_repayment_amount': repay_baselines.loc[user_id, ('amount', 'mean')],
                    'repayment_count': repay_baselines.loc[user_id, ('amount', 'count')],
                    'late_payment_count': repay_baselines.loc[user_id, ('status', '<lambda>')]
                })
        
        return baselines
    
    def check_transaction_rules(self, data: Dict[str, pd.DataFrame], baselines: Dict) -> List[Dict]:
        """Check transaction-based fraud rules"""
        flagged = []
        
        if data['transactions'].empty:
            return flagged
        
        # Rule 1: Multiple credits in short time window
        credits = data['transactions'][data['transactions']['type'] == 'credit'].copy()
        if not credits.empty:
            credits['time_window'] = credits.groupby('user_id')['timestamp'].diff()
            multiple_credits = credits[credits['time_window'] <= timedelta(minutes=self.config.MULTIPLE_CREDITS_WINDOW_MINUTES)]
            
            for _, row in multiple_credits.iterrows():
                flagged.append({
                    'type': 'transaction',
                    'ref_id': row['txn_id'],
                    'user_id': row['user_id'],
                    'rule': 'multiple_credits_short_window',
                    'score': 20,
                    'reason': f"Multiple credits within {self.config.MULTIPLE_CREDITS_WINDOW_MINUTES} minutes"
                })
        
        # Rule 2: Debit amount > account balance (rejection)
        debits = data['transactions'][data['transactions']['type'] == 'debit'].copy()
        if not debits.empty:
            rejections = debits[debits['amount'] > debits['account_balance']]
            
            for _, row in rejections.iterrows():
                flagged.append({
                    'type': 'transaction',
                    'ref_id': row['txn_id'],
                    'user_id': row['user_id'],
                    'rule': 'debit_exceeds_balance',
                    'score': 25,
                    'reason': f"Debit amount {row['amount']} exceeds account balance {row['account_balance']}"
                })
        
        # Rule 3: Unusual transaction amounts (Z-score > 3)
        for user_id, group in data['transactions'].groupby('user_id'):
            if user_id in baselines and 'std_transaction_amount' in baselines[user_id]:
                std_amount = baselines[user_id]['std_transaction_amount']
                mean_amount = baselines[user_id]['avg_transaction_amount']
                
                if std_amount > 0:  # Avoid division by zero
                    z_scores = abs((group['amount'] - mean_amount) / std_amount)
                    unusual = group[z_scores > self.config.Z_SCORE_THRESHOLD]
                    
                    for _, row in unusual.iterrows():
                        flagged.append({
                            'type': 'transaction',
                            'ref_id': row['txn_id'],
                            'user_id': row['user_id'],
                            'rule': 'unusual_amount',
                            'score': 15,
                            'reason': f"Transaction amount {row['amount']} is {z_scores[row.name]:.2f} standard deviations from mean"
                        })
        
        # Rule 4: Nighttime transactions (between 11 PM and 5 AM)
        data['transactions']['hour'] = data['transactions']['timestamp'].dt.hour
        nighttime = data['transactions'][
            (data['transactions']['hour'] >= 23) | 
            (data['transactions']['hour'] <= 5)
        ]
        
        for _, row in nighttime.iterrows():
            flagged.append({
                'type': 'transaction',
                'ref_id': row['txn_id'],
                'user_id': row['user_id'],
                'rule': 'nighttime_transaction',
                'score': 10,
                'reason': f"Transaction at unusual hour: {row['timestamp'].strftime('%H:%M')}"
            })
        
        # Rule 5: High account balance (>2x average)
        for user_id, group in data['transactions'].groupby('user_id'):
            if user_id in baselines and 'avg_account_balance' in baselines[user_id]:
                avg_balance = baselines[user_id]['avg_account_balance']
                high_balance = group[group['account_balance'] > 2 * avg_balance]
                
                for _, row in high_balance.iterrows():
                    flagged.append({
                        'type': 'transaction',
                        'ref_id': row['txn_id'],
                        'user_id': row['user_id'],
                        'rule': 'high_account_balance',
                        'score': 12,
                        'reason': f"Account balance {row['account_balance']} is >2x average {avg_balance}"
                    })
        
        # Rule 6: Unknown payment method
        unknown_payment = data['transactions'][data['transactions']['payment_method'] == 'unknown']
        
        for _, row in unknown_payment.iterrows():
            flagged.append({
                'type': 'transaction',
                'ref_id': row['txn_id'],
                'user_id': row['user_id'],
                'rule': 'unknown_payment_method',
                'score': 8,
                'reason': "Payment method is 'unknown'"
            })
        
        return flagged
    
    def check_loan_rules(self, data: Dict[str, pd.DataFrame], baselines: Dict) -> List[Dict]:
        """Check loan request fraud rules"""
        flagged = []
        
        if data['loan_requests'].empty:
            return flagged
        
        # Rule 1: Multiple loan requests in 24 hours
        data['loan_requests']['date'] = data['loan_requests']['request_timestamp'].dt.date
        daily_requests = data['loan_requests'].groupby(['user_id', 'date']).size()
        multiple_requests = daily_requests[daily_requests > self.config.LOAN_REQUESTS_24H_LIMIT]
        
        for (user_id, date), count in multiple_requests.items():
            user_loans = data['loan_requests'][
                (data['loan_requests']['user_id'] == user_id) & 
                (data['loan_requests']['date'] == date)
            ]
            
            for _, row in user_loans.iterrows():
                flagged.append({
                    'type': 'loan',
                    'ref_id': row['loan_id'],
                    'user_id': row['user_id'],
                    'rule': 'multiple_loan_requests_24h',
                    'score': 18,
                    'reason': f"{count} loan requests in 24 hours"
                })
        
        # Rule 2: Loan amount vs credit history
        if not data['credit_history'].empty:
            for _, loan in data['loan_requests'].iterrows():
                user_credit = data['credit_history'][data['credit_history']['user_id'] == loan['user_id']]
                if not user_credit.empty:
                    credit_score = user_credit.iloc[0]['credit_score']
                    loan_amount = loan['amount_requested']
                    
                    # High loan amount relative to credit score
                    credit_score_num = pd.to_numeric(credit_score, errors='coerce')
                    if credit_score_num < 650 and loan_amount > 10000:
                        flagged.append({
                            'type': 'loan',
                            'ref_id': loan['loan_id'],
                            'user_id': loan['user_id'],
                            'rule': 'high_loan_low_credit',
                            'score': 22,
                            'reason': f"Loan amount {loan_amount} high for credit score {credit_score}"
                        })
        
        return flagged
    
    def check_credit_rules(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Check credit history fraud rules"""
        flagged = []
        
        if data['credit_history'].empty:
            return flagged
        
        # Rule 1: Multiple defaults
        data['credit_history']['defaults_count'] = pd.to_numeric(data['credit_history']['defaults_count'], errors='coerce')
        multiple_defaults = data['credit_history'][data['credit_history']['defaults_count'] > 1]
        
        for _, row in multiple_defaults.iterrows():
            flagged.append({
                'type': 'user',
                'ref_id': row['user_id'],  # Using user_id as ref_id for user-level flags
                'user_id': row['user_id'],
                'rule': 'multiple_defaults',
                'score': 25,
                'reason': f"User has {row['defaults_count']} defaults"
            })
        
        # Rule 2: Credit score drop (would need historical data, simplified here)
        data['credit_history']['credit_score'] = pd.to_numeric(data['credit_history']['credit_score'], errors='coerce')
        low_credit = data['credit_history'][data['credit_history']['credit_score'] < 500]
        
        for _, row in low_credit.iterrows():
            flagged.append({
                'type': 'user',
                'ref_id': row['user_id'],
                'user_id': row['user_id'],
                'rule': 'low_credit_score',
                'score': 15,
                'reason': f"Very low credit score: {row['credit_score']}"
            })
        
        return flagged
    
    def check_kyc_rules(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Check KYC fraud rules"""
        flagged = []
        
        if data['kyc'].empty:
            return flagged
        
        # Rule 1: Unverified status
        unverified = data['kyc'][data['kyc']['verified_status'] == False]
        
        for _, row in unverified.iterrows():
            flagged.append({
                'type': 'user',
                'ref_id': row['user_id'],
                'user_id': row['user_id'],
                'rule': 'unverified_kyc',
                'score': 20,
                'reason': "KYC verification status is false"
            })
        
        return flagged
    
    def check_repayment_rules(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Check repayment fraud rules"""
        flagged = []
        
        if data['repayments'].empty:
            return flagged
        
        # Rule 1: Multiple late payments
        late_payments = data['repayments'][data['repayments']['status'] == 'late']
        late_count = late_payments.groupby('user_id').size()
        multiple_late = late_count[late_count > self.config.LATE_PAYMENTS_THRESHOLD]
        
        for user_id, count in multiple_late.items():
            user_late = late_payments[late_payments['user_id'] == user_id]
            
            for _, row in user_late.iterrows():
                flagged.append({
                    'type': 'repayment',
                    'ref_id': row['repayment_id'],
                    'user_id': row['user_id'],
                    'rule': 'multiple_late_payments',
                    'score': 18,
                    'reason': f"User has {count} late payments"
                })
        
        # Rule 2: Duplicate repayment IDs (shouldn't happen with UUID, but checking)
        duplicate_ids = data['repayments']['repayment_id'].duplicated()
        if duplicate_ids.any():
            duplicates = data['repayments'][duplicate_ids]
            
            for _, row in duplicates.iterrows():
                flagged.append({
                    'type': 'repayment',
                    'ref_id': row['repayment_id'],
                    'user_id': row['user_id'],
                    'rule': 'duplicate_repayment_id',
                    'score': 30,
                    'reason': "Duplicate repayment ID detected"
                })
        
        return flagged
    
    def calculate_risk_score(self, flagged_items: List[Dict]) -> List[Dict]:
        """Calculate final risk scores for flagged items"""
        # Group by user and type to calculate combined scores
        user_scores = {}
        
        for item in flagged_items:
            key = (item['user_id'], item['type'])
            if key not in user_scores:
                user_scores[key] = {
                    'items': [],
                    'total_score': 0,
                    'rules': []
                }
            
            user_scores[key]['items'].append(item)
            user_scores[key]['total_score'] += item['score']
            user_scores[key]['rules'].append(item['rule'])
        
        # Calculate final scores with weights
        final_flagged = []
        for (user_id, item_type), data in user_scores.items():
            # Apply scoring weights
            stats_score = data['total_score'] * self.config.STATS_WEIGHT
            rules_score = data['total_score'] * self.config.RULES_WEIGHT
            new_checks_score = data['total_score'] * self.config.NEW_CHECKS_WEIGHT
            
            final_score = min(stats_score + rules_score + new_checks_score, 100)
            
            if final_score >= self.config.RISK_SCORE_THRESHOLD:
                for item in data['items']:
                    final_flagged.append({
                        'type': item['type'],
                        'ref_id': item['ref_id'],
                        'user_id': item['user_id'],
                        'score': round(final_score, 2),
                        'reasons': data['rules'],
                        'status': 'pending'
                    })
        
        return final_flagged
    
    def save_flagged_items(self, flagged_items: List[Dict]):
        """Save flagged items to database"""
        if not self.conn:
            self.connect_db()
        
        cursor = self.conn.cursor()
        
        try:
            for item in flagged_items:
                cursor.execute("""
                    INSERT INTO flagged_items (type, ref_id, user_id, score, reasons, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    item['type'],
                    item['ref_id'],
                    item['user_id'],
                    item['score'],
                    json.dumps(item['reasons']),
                    item['status']
                ))
            
            self.conn.commit()
            logger.info(f"Saved {len(flagged_items)} flagged items to database")
        except Exception as e:
            logger.error(f"Error saving flagged items: {e}")
            self.conn.rollback()
            raise
        finally:
            cursor.close()
    
    def run_detection(self, days_back: int = 30) -> Dict[str, Any]:
        """Main detection pipeline"""
        try:
            logger.info(f"Starting fraud detection for last {days_back} days")
            
            # Connect to database
            self.connect_db()
            
            # Get data
            data = self.get_data_for_detection(days_back)
            
            # Calculate baselines
            baselines = self.calculate_user_baselines(data)
            
            # Run all rule checks
            all_flagged = []
            all_flagged.extend(self.check_transaction_rules(data, baselines))
            all_flagged.extend(self.check_loan_rules(data, baselines))
            all_flagged.extend(self.check_credit_rules(data))
            all_flagged.extend(self.check_kyc_rules(data))
            all_flagged.extend(self.check_repayment_rules(data))
            
            # Calculate final risk scores
            final_flagged = self.calculate_risk_score(all_flagged)
            
            # Save to database
            if final_flagged:
                self.save_flagged_items(final_flagged)
            
            result = {
                'total_flagged': len(final_flagged),
                'flagged_by_type': {},
                'flagged_by_user': {},
                'high_risk_count': len([f for f in final_flagged if f['score'] >= 85])
            }
            
            # Group by type
            for item in final_flagged:
                item_type = item['type']
                if item_type not in result['flagged_by_type']:
                    result['flagged_by_type'][item_type] = 0
                result['flagged_by_type'][item_type] += 1
            
            # Group by user
            for item in final_flagged:
                user_id = item['user_id']
                if user_id not in result['flagged_by_user']:
                    result['flagged_by_user'][user_id] = 0
                result['flagged_by_user'][user_id] += 1
            
            logger.info(f"Detection completed: {result['total_flagged']} items flagged")
            return result
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            raise
        finally:
            self.close_db()
    
    def run_detection_by_type(self, data_type: str, days_back: int = 30) -> Dict:
        """Run fraud detection for a specific data type only"""
        try:
            # Ensure database connection is open
            if not self.conn:
                self.connect_db()
            
            # Get data for detection
            data = self.get_data_for_detection(days_back)
            
            # Check if the requested data type has data
            if data[data_type].empty:
                logger.warning(f"No {data_type} data found for the last {days_back} days")
                return {
                    'total_flagged': 0,
                    'flagged_by_type': {},
                    'flagged_by_user': {},
                    'high_risk_count': 0,
                    'data_type': data_type
                }
            
            # Calculate baselines for the specific data type
            baselines = self.calculate_user_baselines(data)
            
            # Run specific rule checks based on data type
            all_flagged = []
            
            if data_type == 'transactions':
                all_flagged.extend(self.check_transaction_rules(data, baselines))
            elif data_type == 'loan_requests':
                all_flagged.extend(self.check_loan_rules(data, baselines))
            elif data_type == 'credit_history':
                all_flagged.extend(self.check_credit_rules(data))
            elif data_type == 'kyc':
                all_flagged.extend(self.check_kyc_rules(data))
            elif data_type == 'repayments':
                all_flagged.extend(self.check_repayment_rules(data))
            
            # Calculate final risk scores
            final_flagged = self.calculate_risk_score(all_flagged)
            
            # Save to database
            if final_flagged:
                self.save_flagged_items(final_flagged)
            
            result = {
                'total_flagged': len(final_flagged),
                'flagged_by_type': {data_type: len(final_flagged)},
                'flagged_by_user': {},
                'high_risk_count': len([f for f in final_flagged if f['score'] >= 85]),
                'data_type': data_type
            }
            
            # Group by user
            for item in final_flagged:
                user_id = item['user_id']
                if user_id not in result['flagged_by_user']:
                    result['flagged_by_user'][user_id] = 0
                result['flagged_by_user'][user_id] += 1
            
            logger.info(f"Detection completed for {data_type}: {result['total_flagged']} items flagged")
            return result
            
        except Exception as e:
            logger.error(f"Detection failed for {data_type}: {e}")
            raise
        finally:
            self.close_db()

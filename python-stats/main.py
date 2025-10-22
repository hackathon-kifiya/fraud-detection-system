from flask import Flask, jsonify, request
import math
import statistics
import os
import psycopg2
from datetime import datetime, timedelta
from collections import Counter, defaultdict

app = Flask(__name__)

def get_db_connection():
    url = os.getenv('DATABASE_URL', 'postgresql://frauduser:fraudpass@postgres:5432/frauddb')
    return psycopg2.connect(url)

@app.get('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'python-stats'
    })

@app.post('/analyze')
def analyze():
    data = request.get_json(silent=True) or {}
    days_back = int(data.get('days_back', 30))
    data_type = (data.get('data_type') or '').lower()

    # Load data from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        if data_type == 'transactions':
            cursor.execute("""
                SELECT amount, timestamp, type, payment_method 
                FROM transactions 
                WHERE timestamp >= %s 
                ORDER BY timestamp DESC
            """, (cutoff,))
            rows = cursor.fetchall()
            amounts = [float(row[0]) for row in rows]
            timestamps = [row[1].isoformat() for row in rows]
            data.update({'amounts': amounts, 'timestamps': timestamps})
            
        elif data_type == 'repayments':
            cursor.execute("""
                SELECT amount, timestamp, status 
                FROM repayments 
                WHERE timestamp >= %s 
                ORDER BY timestamp DESC
            """, (cutoff,))
            rows = cursor.fetchall()
            amounts = [float(row[0]) for row in rows]
            timestamps = [row[1].isoformat() for row in rows]
            statuses = [row[2] for row in rows]
            data.update({'amounts': amounts, 'timestamps': timestamps, 'statuses': statuses})
            
        elif data_type == 'credit_history':
            cursor.execute("""
                SELECT credit_score, defaults_count, updated_at 
                FROM credit_history 
                WHERE updated_at >= %s 
                ORDER BY updated_at DESC
            """, (cutoff,))
            rows = cursor.fetchall()
            scores = [int(row[0]) for row in rows]
            defaults = [int(row[1]) for row in rows]
            data.update({'credit_scores': scores, 'defaults_count': defaults})
            
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    def compute_benford(amounts):
        digits = [int(str(abs(a)).lstrip('0.')[0]) for a in amounts if isinstance(a, (int, float)) and a != 0]
        freq = Counter(digits)
        total = sum(freq.values()) or 1
        observed = {d: freq.get(d, 0) / total for d in range(1, 10)}
        expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}
        mad = sum(abs(observed[d] - expected[d]) for d in range(1, 10)) / 9.0
        chi_square = sum(((freq.get(d, 0) - total * expected[d]) ** 2) / (total * expected[d]) for d in range(1, 10)) if total > 0 else 0.0
        return {
            'observed': observed,
            'expected': expected,
            'mad': mad,
            'chi_square': chi_square,
            'n': total
        }

    def compute_zscores(values):
        values = [v for v in values if isinstance(v, (int, float))]
        if len(values) < 2:
            return {'mean': None, 'stdev': None, 'zscores': [], 'anomalies_idx': []}
        mean_val = statistics.fmean(values)
        stdev_val = statistics.pstdev(values) or 1e-9
        zscores = [(v - mean_val) / stdev_val for v in values]
        anomalies_idx = [i for i, z in enumerate(zscores) if abs(z) >= 3.0]
        return {'mean': mean_val, 'stdev': stdev_val, 'zscores': zscores, 'anomalies_idx': anomalies_idx}

    def compute_iqr(values):
        values = sorted([v for v in values if isinstance(v, (int, float))])
        n = len(values)
        if n < 4:
            return {'q1': None, 'q3': None, 'iqr': None, 'upper_fence': None, 'lower_fence': None, 'outliers_idx': []}
        def percentile(p):
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return values[int(k)]
            d0 = values[int(f)] * (c - k)
            d1 = values[int(c)] * (k - f)
            return d0 + d1
        q1 = percentile(0.25)
        q3 = percentile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers_idx = [i for i, v in enumerate(values) if v < lower or v > upper]
        return {'q1': q1, 'q3': q3, 'iqr': iqr, 'upper_fence': upper, 'lower_fence': lower, 'outliers_idx': outliers_idx}

    def compute_velocity(timestamps_iso):
        # events per hour and max spike ratio
        buckets = Counter()
        for ts in timestamps_iso or []:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00')) if isinstance(ts, str) else datetime.utcfromtimestamp(float(ts))
                key = dt.replace(minute=0, second=0, microsecond=0).isoformat()
                buckets[key] += 1
            except Exception:
                continue
        if not buckets:
            return {'avg_per_hour': 0, 'max_per_hour': 0, 'spike_ratio': 0}
        counts = list(buckets.values())
        avg = statistics.fmean(counts)
        mx = max(counts)
        spike_ratio = (mx / avg) if avg > 0 else 0
        return {'avg_per_hour': avg, 'max_per_hour': mx, 'spike_ratio': spike_ratio}

    result = {'summary': {'processed_days': days_back}}

    if data_type == 'transactions':
        amounts = data.get('amounts') or []
        timestamps = data.get('timestamps') or []
        result['transactions'] = {
            'zscore': compute_zscores(amounts),
            'iqr': compute_iqr(amounts),
            'velocity': compute_velocity(timestamps),
            'benford': compute_benford(amounts)
        }
    elif data_type == 'repayments':
        amounts = data.get('amounts') or []
        timestamps = data.get('timestamps') or []
        statuses = [s for s in (data.get('statuses') or []) if isinstance(s, str)]
        late_rate = (sum(1 for s in statuses if s.lower() == 'late') / len(statuses)) if statuses else 0.0
        result['repayments'] = {
            'zscore': compute_zscores(amounts),
            'iqr': compute_iqr(amounts),
            'velocity': compute_velocity(timestamps),
            'late_rate': late_rate
        }
    elif data_type == 'credit_history':
        scores = data.get('credit_scores') or []
        defaults = data.get('defaults_count') or []
        drops = []
        prev = None
        for s in scores:
            if isinstance(s, (int, float)):
                if prev is not None:
                    drops.append(prev - s)
                prev = s
        max_drop = max(drops) if drops else 0
        result['credit_history'] = {
            'zscore': compute_zscores(scores),
            'iqr': compute_iqr(scores),
            'defaults_count': sum(int(x) for x in defaults if isinstance(x, (int, float))),
            'max_score_drop': max_drop
        }
    else:
        # Generic analysis if data_type unspecified
        amounts = data.get('amounts') or []
        timestamps = data.get('timestamps') or []
        result['generic'] = {
            'zscore': compute_zscores(amounts),
            'iqr': compute_iqr(amounts),
            'velocity': compute_velocity(timestamps),
            'benford': compute_benford(amounts)
        }
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)



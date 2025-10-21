from flask import Flask, request, jsonify
import logging
from detection import FraudDetector
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize configuration and detector
config = Config()
detector = FraudDetector(config)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'fraud-detection-engine',
        'version': '1.0.0'
    })

@app.route('/detect', methods=['POST'])
def detect_fraud():
    """Main fraud detection endpoint"""
    try:
        # Parse request data
        data = request.get_json() or {}
        days_back = data.get('days_back', 30)
        
        # Validate input
        if not isinstance(days_back, int) or days_back <= 0:
            return jsonify({
                'error': 'Invalid days_back parameter. Must be a positive integer.'
            }), 400
        
        if days_back > 365:
            return jsonify({
                'error': 'days_back cannot exceed 365 days'
            }), 400
        
        logger.info(f"Starting fraud detection for last {days_back} days")
        
        # Run detection
        result = detector.run_detection(days_back)
        
        logger.info(f"Detection completed successfully: {result['total_flagged']} items flagged")
        
        return jsonify({
            'success': True,
            'message': f'Fraud detection completed for last {days_back} days',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Detection failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during fraud detection',
            'details': str(e)
        }), 500

@app.route('/detect/status', methods=['GET'])
def detection_status():
    """Get detection engine status and configuration"""
    return jsonify({
        'status': 'running',
        'config': {
            'risk_score_threshold': config.RISK_SCORE_THRESHOLD,
            'z_score_threshold': config.Z_SCORE_THRESHOLD,
            'multiple_credits_window_minutes': config.MULTIPLE_CREDITS_WINDOW_MINUTES,
            'loan_requests_24h_limit': config.LOAN_REQUESTS_24H_LIMIT,
            'late_payments_threshold': config.LATE_PAYMENTS_THRESHOLD,
            'credit_score_drop_threshold': config.CREDIT_SCORE_DROP_THRESHOLD,
            'scoring_weights': {
                'stats': config.STATS_WEIGHT,
                'rules': config.RULES_WEIGHT,
                'new_checks': config.NEW_CHECKS_WEIGHT
            }
        }
    })

@app.route('/detect/<data_type>', methods=['POST'])
def detect_fraud_by_type(data_type):
    """Fraud detection for specific data type"""
    try:
        # Validate data type
        valid_types = ['transactions', 'loan_requests', 'credit_history', 'kyc', 'repayments']
        if data_type not in valid_types:
            return jsonify({
                'error': f'Invalid data type: {data_type}. Valid types: {", ".join(valid_types)}'
            }), 400
        
        # Parse request data
        data = request.get_json() or {}
        days_back = data.get('days_back', 30)
        
        # Validate input
        if not isinstance(days_back, int) or days_back <= 0:
            return jsonify({
                'error': 'Invalid days_back parameter. Must be a positive integer.'
            }), 400
        
        if days_back > 365:
            return jsonify({
                'error': 'days_back cannot exceed 365 days'
            }), 400
        
        logger.info(f"Starting fraud detection for {data_type} (last {days_back} days)")
        
        # Run detection for specific data type
        result = detector.run_detection_by_type(data_type, days_back)
        
        logger.info(f"Detection completed for {data_type}: {result['total_flagged']} items flagged")
        
        return jsonify({
            'success': True,
            'message': f'Fraud detection completed for {data_type}',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error in fraud detection for {data_type}: {e}")
        return jsonify({
            'error': f'Detection failed: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /health',
            'POST /detect',
            'GET /detect/status'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'Check the API documentation for correct HTTP methods'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Fraud Detection Engine")
    logger.info(f"Database: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    logger.info(f"Risk threshold: {config.RISK_SCORE_THRESHOLD}")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.DEBUG
    )

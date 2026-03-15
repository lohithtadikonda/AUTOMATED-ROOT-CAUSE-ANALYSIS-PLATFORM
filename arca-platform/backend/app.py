"""
ARCA Platform - Main Application Entry Point
Automated Root Cause Analysis Platform for Deployment Errors
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
import jwt
import requests as http_requests
from functools import wraps

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from anomaly_detector import AnomalyDetector, Threshold
from rca_engine import RCAEngine
from log_collector import LogCollector
from metric_collector import MetricCollector
from event_correlator import EventCorrelator
from recommendation_engine import RecommendationEngine
from alert_system import AlertSystem

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# MongoDB connection
try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    db = mongo_client[os.getenv('MONGODB_DB_NAME', 'arca_db')]
    print("[OK] MongoDB connected successfully")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    db = None

# Initialize ARCA components
thresholds = {
    'cpu_usage': Threshold(min_value=0, max_value=float(os.getenv('CPU_THRESHOLD', 80))),
    'memory_usage': Threshold(min_value=0, max_value=float(os.getenv('MEMORY_THRESHOLD', 85))),
    'response_time': Threshold(min_value=0, max_value=float(os.getenv('RESPONSE_TIME_THRESHOLD', 2000))),
    'error_rate': Threshold(min_value=0, max_value=float(os.getenv('ERROR_RATE_THRESHOLD', 5))),
}

anomaly_detector = AnomalyDetector(thresholds)
rca_engine = RCAEngine([])
event_correlator = EventCorrelator(window_size_minutes=5)
recommendation_engine = RecommendationEngine({})
alert_system = AlertSystem()

# ==========================
# Clerk JWT Auth Middleware
# ==========================

_jwks_cache = {}

def _get_jwks():
    """Fetch Clerk's public keys (cached)."""
    jwks_url = os.getenv('CLERK_JWKS_URL')
    if not jwks_url:
        return None
    if _jwks_cache.get('keys'):
        return _jwks_cache['keys']
    try:
        resp = http_requests.get(jwks_url, timeout=5)
        resp.raise_for_status()
        _jwks_cache['keys'] = resp.json().get('keys', [])
        return _jwks_cache['keys']
    except Exception:
        return None


def _verify_token(token):
    """Verify Clerk JWT and return payload, or None on failure."""
    keys = _get_jwks()
    if not keys:
        # CLERK_JWKS_URL not configured — skip auth (dev mode)
        return {'sub': 'dev', 'public_metadata': {'role': 'admin'}}
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        public_key = None
        for key_data in keys:
            if key_data.get('kid') == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
                break
        if public_key is None:
            return None
        payload = jwt.decode(token, public_key, algorithms=['RS256'], options={'verify_aud': False})
        return payload
    except Exception:
        return None


def require_auth(f):
    """Decorator: requires a valid Clerk JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        token = auth_header.split(' ', 1)[1]
        payload = _verify_token(token)
        if payload is None:
            return jsonify({'error': 'Invalid or expired token'}), 401
        request.clerk_user = payload
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """Decorator: requires admin role in Clerk public metadata."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        token = auth_header.split(' ', 1)[1]
        payload = _verify_token(token)
        if payload is None:
            return jsonify({'error': 'Invalid or expired token'}), 401
        role = (payload.get('public_metadata') or {}).get('role', '')
        if role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        request.clerk_user = payload
        return f(*args, **kwargs)
    return decorated


# ==========================
# Health & Status Endpoints
# ==========================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ARCA Backend',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db is not None else 'disconnected'
    }), 200


@app.route('/api/system-health', methods=['GET'])
def get_system_health():
    """Get overall system health status"""
    try:
        anomaly_count = db.anomalies.count_documents({}) if db is not None else 0
        rca_count = db.rca_results.count_documents({}) if db is not None else 0
        
        # Get recent anomalies
        recent_anomalies = []
        if db is not None:
            anomalies = list(db.anomalies.find().sort('timestamp', -1).limit(5))
            for anomaly in anomalies:
                anomaly['_id'] = str(anomaly['_id'])
                recent_anomalies.append(anomaly)
        
        # Get current metrics
        metric_collector = MetricCollector(interval=10)
        current_metrics = metric_collector.get_metric_snapshot()
        
        return jsonify({
            'status': 'ok',
            'statistics': {
                'total_anomalies': anomaly_count,
                'total_rca_reports': rca_count,
            },
            'current_metrics': current_metrics,
            'recent_anomalies': recent_anomalies
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# Anomaly Detection Endpoints
# ==========================

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    """Get all anomalies with optional filtering"""
    try:
        # Query parameters
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 50))
        
        query = {}
        if severity:
            query['severity'] = severity.upper()
        
        if db is not None:
            anomalies = list(db.anomalies.find(query).sort('timestamp', -1).limit(limit))
            for anomaly in anomalies:
                anomaly['_id'] = str(anomaly['_id'])
        else:
            anomalies = []
        
        return jsonify({
            'total': len(anomalies),
            'anomalies': anomalies
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect', methods=['POST'])
def detect_anomalies():
    """Detect anomalies from logs and metrics"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Detect log anomalies
        logs = data.get('logs', [])
        log_anomalies = anomaly_detector.detect_log_anomalies(logs) if logs else []
        
        # Detect metric anomalies
        metrics = data.get('metrics', {})
        metric_anomalies = anomaly_detector.detect_metric_anomalies(metrics) if metrics else []
        
        # Store in database
        all_anomalies = log_anomalies + metric_anomalies
        if db is not None and all_anomalies:
            for anomaly in all_anomalies:
                db.anomalies.insert_one(anomaly.to_dict())
        
        # Trigger RCA if critical anomalies detected
        critical_anomalies = [a for a in all_anomalies if a.severity == 'CRITICAL']
        if critical_anomalies:
            # Correlate events
            correlated = event_correlator.correlate_anomalies(all_anomalies)
            
            # Perform RCA
            if correlated:
                rca_result = rca_engine.analyze_root_cause(correlated)
                if db is not None:
                    db.rca_results.insert_one({
                        'root_cause': rca_result.root_cause,
                        'confidence': rca_result.confidence,
                        'affected_components': rca_result.affected_components,
                        'recommendations': rca_result.recommendations,
                        'timestamp': rca_result.timestamp.isoformat()
                    })
                
                # Send alerts
                alert_system.send_alert({
                    'type': 'CRITICAL_ANOMALY',
                    'root_cause': rca_result.root_cause,
                    'confidence': rca_result.confidence,
                    'anomaly_count': len(critical_anomalies)
                })
        
        return jsonify({
            'detected_anomalies': len(all_anomalies),
            'log_anomalies': [a.to_dict() for a in log_anomalies],
            'metric_anomalies': [a.to_dict() for a in metric_anomalies],
            'critical_count': len(critical_anomalies)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# RCA (Root Cause Analysis) Endpoints
# ==========================

@app.route('/api/rca/analyze', methods=['POST'])
def analyze_root_cause():
    """Perform root cause analysis on provided anomalies"""
    try:
        data = request.json
        anomaly_ids = data.get('anomaly_ids', [])
        
        if not anomaly_ids:
            return jsonify({'error': 'No anomaly IDs provided'}), 400
        
        # Fetch anomalies from database
        anomalies = []
        if db is not None:
            for anomaly_id in anomaly_ids:
                anomaly_data = db.anomalies.find_one({'id': anomaly_id})
                if anomaly_data:
                    anomalies.append(anomaly_data)
        
        if not anomalies:
            return jsonify({'error': 'No valid anomalies found'}), 404
        
        # Correlate events
        correlated = event_correlator.correlate_anomalies(anomalies)
        
        # Perform RCA
        rca_result = rca_engine.analyze_root_cause(correlated)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(rca_result)
        
        # Store result
        result_dict = {
            'root_cause': rca_result.root_cause,
            'confidence': rca_result.confidence,
            'affected_components': rca_result.affected_components,
            'causal_chain': rca_result.causal_chain,
            'recommendations': [r['action'] for r in recommendations],
            'timestamp': rca_result.timestamp.isoformat()
        }
        
        if db is not None:
            db.rca_results.insert_one(result_dict)
        
        return jsonify(result_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rca-reports', methods=['GET'])
def get_rca_reports():
    """Get all RCA analysis reports"""
    try:
        limit = int(request.args.get('limit', 20))
        
        if db is not None:
            reports = list(db.rca_results.find().sort('timestamp', -1).limit(limit))
            for report in reports:
                report['_id'] = str(report['_id'])
        else:
            reports = []
        
        return jsonify({
            'total_reports': len(reports),
            'reports': reports
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rca-reports/<report_id>', methods=['GET'])
def get_rca_report_detail(report_id):
    """Get detailed RCA report by ID"""
    try:
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        report = db.rca_results.find_one({'_id': report_id})
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        report['_id'] = str(report['_id'])
        
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# Log Collection Endpoints
# ==========================

@app.route('/api/logs/upload', methods=['POST'])
def upload_logs():
    """Upload and parse log files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Save temporarily
        temp_path = f'/tmp/{file.filename}'
        file.save(temp_path)
        
        # Parse logs
        log_collector = LogCollector(log_file_path=temp_path, interval=1)
        logs = log_collector.read_new_logs()
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'logs_parsed': len(logs),
            'logs': logs
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# Metrics Endpoints
# ==========================

@app.route('/api/metrics/current', methods=['GET'])
def get_current_metrics():
    """Get current system metrics"""
    try:
        metric_collector = MetricCollector(interval=10)
        metrics = metric_collector.get_metric_snapshot()
        
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/history', methods=['GET'])
def get_metrics_history():
    """Get historical metrics"""
    try:
        limit = int(request.args.get('limit', 100))
        
        if db is not None:
            metrics = list(db.metrics.find().sort('timestamp', -1).limit(limit))
            for metric in metrics:
                metric['_id'] = str(metric['_id'])
        else:
            metrics = []
        
        return jsonify({
            'total': len(metrics),
            'metrics': metrics
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# Alert Endpoints
# ==========================

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    try:
        if db is not None:
            alerts = list(db.alerts.find().sort('timestamp', -1).limit(50))
            for alert in alerts:
                alert['_id'] = str(alert['_id'])
        else:
            alerts = []
        
        return jsonify({
            'total': len(alerts),
            'alerts': alerts
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/acknowledge', methods=['POST'])
def acknowledge_alert():
    """Acknowledge an alert"""
    try:
        data = request.json
        alert_id = data.get('alert_id')
        
        if not alert_id:
            return jsonify({'error': 'No alert ID provided'}), 400
        
        if db is not None:
            result = db.alerts.update_one(
                {'id': alert_id},
                {'$set': {
                    'acknowledged': True,
                    'acknowledged_at': datetime.now().isoformat()
                }}
            )
            
            if result.modified_count > 0:
                return jsonify({'message': 'Alert acknowledged'}), 200
            else:
                return jsonify({'error': 'Alert not found'}), 404
        else:
            return jsonify({'error': 'Database not available'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# Statistics Endpoints
# ==========================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get platform statistics"""
    try:
        if db is None:
            return jsonify({'error': 'Database not available'}), 500
        
        stats = {
            'total_anomalies': db.anomalies.count_documents({}),
            'total_rca_reports': db.rca_results.count_documents({}),
            'total_alerts': db.alerts.count_documents({}),
            'critical_anomalies': db.anomalies.count_documents({'severity': 'CRITICAL'}),
            'high_anomalies': db.anomalies.count_documents({'severity': 'HIGH'}),
            'medium_anomalies': db.anomalies.count_documents({'severity': 'MEDIUM'}),
            'low_anomalies': db.anomalies.count_documents({'severity': 'LOW'}),
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# Error Handlers
# ==========================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


# ==========================
# Main Entry Point
# ==========================

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    
    print("=" * 50)
    print("ARCA Platform Backend Starting...")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Database: {os.getenv('MONGODB_DB_NAME', 'arca_db')}")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

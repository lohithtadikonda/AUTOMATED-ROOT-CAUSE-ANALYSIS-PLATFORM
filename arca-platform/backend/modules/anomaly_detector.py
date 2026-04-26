# DONE BY PRIYANSHU kumar (2301163)

from typing import List, Dict, Optional
from datetime import datetime
import statistics


class Anomaly:
    def __init__(self, anomaly_type: str, severity: str, value: float, 
                 metric_name: str, timestamp: datetime, description: str):
        self.anomaly_type = anomaly_type
        self.severity = severity
        self.value = value
        self.metric_name = metric_name
        self.timestamp = timestamp
        self.description = description
        self.id = f"{metric_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.anomaly_type,
            'severity': self.severity,
            'value': self.value,
            'metric': self.metric_name,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description
        }


class Threshold:
    def __init__(self, min_value: Optional[float] = None, 
                 max_value: Optional[float] = None,
                 std_dev_multiplier: float = 2.0):
        self.min_value = min_value
        self.max_value = max_value
        self.std_dev_multiplier = std_dev_multiplier


class AnomalyDetector:
    
    def __init__(self, thresholds: Dict[str, Threshold]):
        if not isinstance(thresholds, dict):
            raise ValueError("Thresholds must be a dictionary")
        
        self.thresholds = thresholds
        self.detection_algorithm = "hybrid"
        self.anomaly_history: List[Anomaly] = []
        self._baseline_data: Dict[str, List[float]] = {}
    
    def detect_log_anomalies(self, logs: List[Dict]) -> List[Anomaly]:
        if not logs:
            return []
        
        anomalies = []
        error_count = 0
        critical_count = 0
        deployment_keywords = [
            'deployment failed', 'deploy error', 'rollback', 
            'connection refused', 'connection timeout', 'request timeout', 'out of memory',
            'permission denied', 'authentication failed'
        ]
        
        for log in logs:
            level = log.get('level', '').upper()
            message = log.get('message', '')
            timestamp = log.get('timestamp')
            
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except:
                    timestamp = datetime.now()
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.now()
            
            message_lower = message.lower()
            
            if level == 'ERROR':
                error_count += 1
                severity = 'HIGH'
                
                for keyword in deployment_keywords:
                    if keyword in message_lower:
                        severity = 'CRITICAL'
                        break
                
                anomaly = self._create_anomaly_record(
                    anomaly_type='LOG_ERROR',
                    severity=severity,
                    value=1.0,
                    metric_name='error_logs',
                    timestamp=timestamp,
                    description=f"Error in logs: {message[:100]}"
                )
                anomalies.append(anomaly)
            
            elif level == 'CRITICAL':
                critical_count += 1
                anomaly = self._create_anomaly_record(
                    anomaly_type='LOG_CRITICAL',
                    severity='CRITICAL',
                    value=1.0,
                    metric_name='critical_logs',
                    timestamp=timestamp,
                    description=f"Critical error: {message[:100]}"
                )
                anomalies.append(anomaly)
            
            elif level in ['WARNING', 'WARN', 'INFO']:
                for keyword in deployment_keywords:
                    if keyword in message_lower:
                        anomaly = self._create_anomaly_record(
                            anomaly_type='DEPLOYMENT_ERROR',
                            severity='MEDIUM',
                            value=0.5,
                            metric_name='deployment_logs',
                            timestamp=timestamp,
                            description=f"Deployment issue detected: {keyword}"
                        )
                        anomalies.append(anomaly)
                        break
        
        self.anomaly_history.extend(anomalies)
        return anomalies
    
    def detect_metric_anomalies(self, metrics: Dict[str, float]) -> List[Anomaly]:
        if not metrics:
            return []
        
        anomalies = []
        timestamp = datetime.now()
        
        for metric_name, value in metrics.items():
            threshold = self.thresholds.get(metric_name)
            
            if not threshold:
                continue
            
            if metric_name not in self._baseline_data:
                self._baseline_data[metric_name] = []
            self._baseline_data[metric_name].append(value)
            
            if len(self._baseline_data[metric_name]) > 100:
                self._baseline_data[metric_name] = self._baseline_data[metric_name][-100:]
            
            anomaly_detected = False
            severity = 'LOW'
            description = ""
            
            if threshold.max_value is not None and value > threshold.max_value:
                anomaly_detected = True
                excess = value - threshold.max_value
                percent = (excess / threshold.max_value) * 100
                
                if percent > 50:
                    severity = 'CRITICAL'
                elif percent > 25:
                    severity = 'HIGH'
                elif percent > 10:
                    severity = 'MEDIUM'
                else:
                    severity = 'LOW'
                
                description = f"{metric_name} exceeded threshold: {value:.2f} > {threshold.max_value}"
            
            elif threshold.min_value is not None and value < threshold.min_value:
                anomaly_detected = True
                severity = 'MEDIUM'
                description = f"{metric_name} below threshold: {value:.2f} < {threshold.min_value}"
            
            if not anomaly_detected and len(self._baseline_data[metric_name]) >= 10:
                mean = statistics.mean(self._baseline_data[metric_name])
                stdev = statistics.stdev(self._baseline_data[metric_name])
                
                upper_bound = mean + (threshold.std_dev_multiplier * stdev)
                lower_bound = mean - (threshold.std_dev_multiplier * stdev)
                
                if value > upper_bound:
                    anomaly_detected = True
                    severity = 'MEDIUM'
                    description = f"{metric_name} statistically anomalous: {value:.2f} > {upper_bound:.2f}"
                elif value < lower_bound:
                    anomaly_detected = True
                    severity = 'LOW'
                    description = f"{metric_name} statistically anomalous: {value:.2f} < {lower_bound:.2f}"
            
            if anomaly_detected:
                anomaly = self._create_anomaly_record(
                    anomaly_type='METRIC_ANOMALY',
                    severity=severity,
                    value=value,
                    metric_name=metric_name,
                    timestamp=timestamp,
                    description=description
                )
                anomalies.append(anomaly)
        
        self.anomaly_history.extend(anomalies)
        return anomalies
    
    def set_threshold(self, metric: str, threshold: Threshold):
        self.thresholds[metric] = threshold
    
    def is_anomaly(self, value: float, metric: str) -> bool:
        threshold = self.thresholds.get(metric)
        if not threshold:
            return False
        
        if threshold.max_value is not None and value > threshold.max_value:
            return True
        
        if threshold.min_value is not None and value < threshold.min_value:
            return True
        
        return False
    
    def get_anomaly_history(self, limit: Optional[int] = None) -> List[Anomaly]:
        if limit:
            return self.anomaly_history[-limit:]
        return self.anomaly_history
    
    def clear_history(self):
        self.anomaly_history = []
    
    def _create_anomaly_record(self, anomaly_type: str, severity: str, 
                                value: float, metric_name: str, 
                                timestamp: datetime, description: str) -> Anomaly:
        return Anomaly(
            anomaly_type=anomaly_type,
            severity=severity,
            value=value,
            metric_name=metric_name,
            timestamp=timestamp,
            description=description
        )


if __name__ == "__main__":
    print("Testing AnomalyDetector...")
    
    thresholds = {
        'cpu_usage': Threshold(min_value=0, max_value=80),
        'memory_usage': Threshold(min_value=0, max_value=85),
        'response_time': Threshold(min_value=0, max_value=2000),
    }
    
    detector = AnomalyDetector(thresholds)
    
    test_logs = [
        {'level': 'ERROR', 'message': 'Deployment failed - connection timeout', 'timestamp': datetime.now()},
        {'level': 'INFO', 'message': 'Application started', 'timestamp': datetime.now()},
        {'level': 'CRITICAL', 'message': 'Out of memory', 'timestamp': datetime.now()},
    ]
    
    log_anomalies = detector.detect_log_anomalies(test_logs)
    print(f"Detected {len(log_anomalies)} log anomalies")
    
    test_metrics = {
        'cpu_usage': 95.5,
        'memory_usage': 78.0,
        'response_time': 2500,
    }
    
    metric_anomalies = detector.detect_metric_anomalies(test_metrics)
    print(f"Detected {len(metric_anomalies)} metric anomalies")
    
    print("AnomalyDetector tests passed!")

"""
AnomalyDetector Module
Part C - Module 1 Implementation
CS331 Software Engineering Lab Assignment 3

This module implements anomaly detection for the Automated Root Cause Analysis Platform.
It detects abnormal behavior in system logs and performance metrics.
"""

from typing import List, Dict, Optional
from datetime import datetime
import statistics


class Anomaly:
    """Represents a detected anomaly"""
    def __init__(self, anomaly_type: str, severity: str, value: float, 
                 metric_name: str, timestamp: datetime, description: str):
        self.anomaly_type = anomaly_type
        self.severity = severity  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
        self.value = value
        self.metric_name = metric_name
        self.timestamp = timestamp
        self.description = description
        self.id = f"{metric_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self):
        """Convert anomaly to dictionary"""
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
    """Threshold configuration for anomaly detection"""
    def __init__(self, min_value: Optional[float] = None, 
                 max_value: Optional[float] = None,
                 std_dev_multiplier: float = 2.0):
        self.min_value = min_value
        self.max_value = max_value
        self.std_dev_multiplier = std_dev_multiplier


class AnomalyDetector:
    """
    AnomalyDetector Class
    Detects anomalies in system logs and metrics using threshold-based 
    and statistical methods
    """
    
    def __init__(self, thresholds: Dict[str, Threshold]):
        """
        Initialize AnomalyDetector
        
        Args:
            thresholds: Dictionary mapping metric names to Threshold objects
        """
        if not isinstance(thresholds, dict):
            raise ValueError("Thresholds must be a dictionary")
        
        self.thresholds = thresholds
        self.detection_algorithm = "hybrid"  # threshold + statistical
        self.anomaly_history: List[Anomaly] = []
        self._baseline_data: Dict[str, List[float]] = {}
    
    def detect_log_anomalies(self, logs: List[Dict]) -> List[Anomaly]:
        """
        Detect anomalies in log entries
        
        Args:
            logs: List of log entry dictionaries with 'level', 'message', 'timestamp'
        
        Returns:
            List of detected Anomaly objects
        """
        if not logs:
            return []
        
        anomalies = []
        error_count = 0
        critical_count = 0
        
        for log in logs:
            level = log.get('level', '').upper()
            message = log.get('message', '')
            timestamp = log.get('timestamp', datetime.now())
            
            # Detect ERROR level logs
            if level == 'ERROR':
                error_count += 1
                anomaly = self._create_anomaly_record(
                    anomaly_type='LOG_ERROR',
                    severity='HIGH',
                    value=1.0,
                    metric_name='error_logs',
                    timestamp=timestamp,
                    description=f"Error in logs: {message[:100]}"
                )
                anomalies.append(anomaly)
            
            # Detect CRITICAL level logs
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
            
            # Detect deployment-related keywords
            deployment_keywords = ['deployment failed', 'deploy error', 
                                  'rollback', 'connection refused', 
                                  'timeout', 'out of memory']
            
            if any(keyword in message.lower() for keyword in deployment_keywords):
                anomaly = self._create_anomaly_record(
                    anomaly_type='DEPLOYMENT_ERROR',
                    severity='CRITICAL',
                    value=1.0,
                    metric_name='deployment_errors',
                    timestamp=timestamp,
                    description=f"Deployment issue detected: {message[:100]}"
                )
                anomalies.append(anomaly)
        
        # Store in history
        self.anomaly_history.extend(anomalies)
        
        return anomalies
    
    def detect_metric_anomalies(self, metrics: Dict[str, float]) -> List[Anomaly]:
        """
        Detect anomalies in performance metrics
        
        Args:
            metrics: Dictionary of metric name to value
        
        Returns:
            List of detected Anomaly objects
        """
        if not metrics:
            return []
        
        anomalies = []
        timestamp = datetime.now()
        
        for metric_name, value in metrics.items():
            if metric_name in self.thresholds:
                threshold = self.thresholds[metric_name]
                
                # Threshold-based detection
                if self.is_anomaly(value, metric_name):
                    severity = self._calculate_severity(value, metric_name)
                    
                    anomaly = self._create_anomaly_record(
                        anomaly_type='METRIC_THRESHOLD',
                        severity=severity,
                        value=value,
                        metric_name=metric_name,
                        timestamp=timestamp,
                        description=f"{metric_name} = {value:.2f} exceeds threshold"
                    )
                    anomalies.append(anomaly)
            
            # Update baseline data for statistical analysis
            if metric_name not in self._baseline_data:
                self._baseline_data[metric_name] = []
            self._baseline_data[metric_name].append(value)
            
            # Keep only recent 100 data points
            if len(self._baseline_data[metric_name]) > 100:
                self._baseline_data[metric_name].pop(0)
            
            # Statistical anomaly detection (if enough baseline data)
            if len(self._baseline_data[metric_name]) >= 10:
                if self._apply_statistical_analysis(
                    self._baseline_data[metric_name], value
                ):
                    anomaly = self._create_anomaly_record(
                        anomaly_type='METRIC_STATISTICAL',
                        severity='MEDIUM',
                        value=value,
                        metric_name=metric_name,
                        timestamp=timestamp,
                        description=f"{metric_name} = {value:.2f} is statistically anomalous"
                    )
                    anomalies.append(anomaly)
        
        # Store in history
        self.anomaly_history.extend(anomalies)
        
        return anomalies
    
    def is_anomaly(self, value: float, metric: str) -> bool:
        """
        Check if a value is anomalous based on configured thresholds
        
        Args:
            value: Metric value to check
            metric: Metric name
        
        Returns:
            True if value exceeds threshold, False otherwise
        """
        if metric not in self.thresholds:
            return False
        
        threshold = self.thresholds[metric]
        
        # Check min threshold
        if threshold.min_value is not None and value < threshold.min_value:
            return True
        
        # Check max threshold
        if threshold.max_value is not None and value > threshold.max_value:
            return True
        
        return False
    
    def set_threshold(self, metric: str, threshold: Threshold) -> None:
        """
        Update or add a threshold for a metric
        
        Args:
            metric: Metric name
            threshold: Threshold object
        """
        if not isinstance(threshold, Threshold):
            raise ValueError("threshold must be a Threshold object")
        
        self.thresholds[metric] = threshold
    
    def _apply_statistical_analysis(self, data: List[float], 
                                   new_value: float) -> bool:
        """
        Apply statistical analysis to detect anomalies
        Uses standard deviation method
        
        Args:
            data: Historical data points
            new_value: New value to check
        
        Returns:
            True if new_value is anomalous
        """
        if len(data) < 3:
            return False
        
        try:
            mean = statistics.mean(data)
            std_dev = statistics.stdev(data)
            
            # Get multiplier from threshold if available
            multiplier = 2.0
            for metric, threshold in self.thresholds.items():
                if threshold.std_dev_multiplier:
                    multiplier = threshold.std_dev_multiplier
                    break
            
            # Check if value is beyond N standard deviations
            lower_bound = mean - (multiplier * std_dev)
            upper_bound = mean + (multiplier * std_dev)
            
            return new_value < lower_bound or new_value > upper_bound
            
        except Exception as e:
            print(f"Statistical analysis error: {e}")
            return False
    
    def _create_anomaly_record(self, anomaly_type: str, severity: str, 
                              value: float, metric_name: str, 
                              timestamp: datetime, description: str) -> Anomaly:
        """
        Create an Anomaly object
        
        Args:
            anomaly_type: Type of anomaly
            severity: Severity level
            value: Metric value
            metric_name: Name of metric
            timestamp: When anomaly occurred
            description: Human-readable description
        
        Returns:
            Anomaly object
        """
        return Anomaly(
            anomaly_type=anomaly_type,
            severity=severity,
            value=value,
            metric_name=metric_name,
            timestamp=timestamp,
            description=description
        )
    
    def _calculate_severity(self, value: float, metric: str) -> str:
        """
        Calculate severity based on how much threshold is exceeded
        
        Args:
            value: Metric value
            metric: Metric name
        
        Returns:
            Severity string: "LOW", "MEDIUM", "HIGH", "CRITICAL"
        """
        if metric not in self.thresholds:
            return "MEDIUM"
        
        threshold = self.thresholds[metric]
        
        if threshold.max_value:
            if value > threshold.max_value * 2:
                return "CRITICAL"
            elif value > threshold.max_value * 1.5:
                return "HIGH"
            elif value > threshold.max_value * 1.2:
                return "MEDIUM"
        
        return "LOW"
    
    def get_anomaly_history(self, limit: int = 50) -> List[Anomaly]:
        """Get recent anomalies"""
        return self.anomaly_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear anomaly history"""
        self.anomaly_history.clear()


# Example usage and testing
if __name__ == "__main__":
    print("="*60)
    print("AnomalyDetector Module - Test Cases")
    print("="*60)
    
    # Define thresholds
    thresholds = {
        'cpu_usage': Threshold(min_value=0, max_value=80),
        'memory_usage': Threshold(min_value=0, max_value=85),
        'response_time': Threshold(min_value=0, max_value=2000),  # ms
    }
    
    # Create detector
    detector = AnomalyDetector(thresholds)
    print(f"\n✓ AnomalyDetector initialized with {len(thresholds)} thresholds")
    
    # Test 1: Log anomaly detection
    print("\n" + "="*60)
    print("Test 1: Log Anomaly Detection")
    print("="*60)
    
    logs = [
        {'level': 'INFO', 'message': 'System started', 
         'timestamp': datetime.now()},
        {'level': 'ERROR', 'message': 'Database connection failed', 
         'timestamp': datetime.now()},
        {'level': 'CRITICAL', 'message': 'Deployment failed: timeout error', 
         'timestamp': datetime.now()},
        {'level': 'WARNING', 'message': 'Memory usage at 75%', 
         'timestamp': datetime.now()},
    ]
    
    log_anomalies = detector.detect_log_anomalies(logs)
    print(f"\nProcessed {len(logs)} log entries")
    print(f"Detected {len(log_anomalies)} log anomalies:")
    for anomaly in log_anomalies:
        print(f"  [{anomaly.severity}] {anomaly.anomaly_type}: {anomaly.description}")
    
    # Test 2: Metric anomaly detection
    print("\n" + "="*60)
    print("Test 2: Metric Anomaly Detection")
    print("="*60)
    
    test_metrics = [
        {'cpu_usage': 95.5, 'memory_usage': 70.0, 'response_time': 3500},
        {'cpu_usage': 65.0, 'memory_usage': 90.0, 'response_time': 1500},
        {'cpu_usage': 50.0, 'memory_usage': 60.0, 'response_time': 500},
    ]
    
    for i, metrics in enumerate(test_metrics, 1):
        print(f"\nMetric Set {i}: {metrics}")
        metric_anomalies = detector.detect_metric_anomalies(metrics)
        if metric_anomalies:
            print(f"  Detected {len(metric_anomalies)} anomalies:")
            for anomaly in metric_anomalies:
                print(f"    [{anomaly.severity}] {anomaly.description}")
        else:
            print("  No anomalies detected")
    
    # Test 3: Statistical anomaly detection
    print("\n" + "="*60)
    print("Test 3: Statistical Anomaly Detection")
    print("="*60)
    
    # Build baseline with normal values
    print("\nBuilding baseline with normal CPU usage...")
    for i in range(15):
        detector.detect_metric_anomalies({'cpu_usage': 50 + (i % 5)})
    
    # Now introduce an anomalous value
    print("Introducing anomalous CPU spike...")
    anomalies = detector.detect_metric_anomalies({'cpu_usage': 120})
    
    if anomalies:
        print(f"  Statistical anomaly detected!")
        for a in anomalies:
            if a.anomaly_type == 'METRIC_STATISTICAL':
                print(f"    {a.description}")
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Total anomalies in history: {len(detector.anomaly_history)}")
    print(f"Severity breakdown:")
    
    severity_count = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
    for a in detector.anomaly_history:
        severity_count[a.severity] += 1
    
    for severity, count in severity_count.items():
        if count > 0:
            print(f"  {severity}: {count}")
    
    print("\n" + "="*60)
    print("All tests completed successfully! ✓")
    print("="*60)

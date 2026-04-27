"""
ARCA Platform - Assignment 9: Test Execution
Module Under Test: AnomalyDetector (anomaly_detector.py)

Executes 10 designed test cases and logs results with evidence.
Run:  pytest Assignment9/test_anomaly_detector.py -v --tb=short
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Path setup so we can import the backend modules from the arca-platform tree
# ---------------------------------------------------------------------------
BACKEND_MODULES = os.path.join(
    os.path.dirname(__file__), '..', 'arca-platform', 'backend', 'modules'
)
sys.path.insert(0, os.path.abspath(BACKEND_MODULES))

from anomaly_detector import AnomalyDetector, Anomaly, Threshold


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def default_thresholds():
    """Standard thresholds used across most tests."""
    return {
        'cpu_usage': Threshold(min_value=0, max_value=80),
        'memory_usage': Threshold(min_value=0, max_value=85),
        'response_time': Threshold(min_value=0, max_value=2000),
        'error_rate': Threshold(min_value=0, max_value=5),
    }


@pytest.fixture
def detector(default_thresholds):
    """Fresh AnomalyDetector instance."""
    return AnomalyDetector(default_thresholds)


# ===================================================================
# TC-AD-001: Metric anomaly when CPU exceeds threshold
# ===================================================================

class TestTCAD001:
    """TC-AD-001: Detect metric anomaly when CPU exceeds threshold."""

    def test_cpu_above_threshold(self, detector):
        """CPU at 95.5% should be flagged as METRIC_ANOMALY."""
        metrics = {'cpu_usage': 95.5}
        anomalies = detector.detect_metric_anomalies(metrics)

        assert len(anomalies) == 1, f"Expected 1 anomaly, got {len(anomalies)}"
        a = anomalies[0]
        assert a.anomaly_type == 'METRIC_ANOMALY'
        assert a.metric_name == 'cpu_usage'
        assert a.value == 95.5
        # Excess = 15.5, percent_excess = 19.375% => MEDIUM band (>10%, <=25%)
        assert a.severity == 'MEDIUM', f"Expected MEDIUM, got {a.severity}"
        print(f"[TC-AD-001] PASS  | severity={a.severity}, value={a.value}")


# ===================================================================
# TC-AD-002: No anomaly for normal metrics
# ===================================================================

class TestTCAD002:
    """TC-AD-002: No anomaly for normal metric values."""

    def test_normal_metrics(self, detector):
        """CPU=45, Memory=60 are within limits => 0 anomalies."""
        metrics = {'cpu_usage': 45.0, 'memory_usage': 60.0}
        anomalies = detector.detect_metric_anomalies(metrics)

        assert len(anomalies) == 0, f"Expected 0 anomalies, got {len(anomalies)}"
        print("[TC-AD-002] PASS  | 0 anomalies for normal values")


# ===================================================================
# TC-AD-003: CRITICAL severity for > 50% excess
# ===================================================================

class TestTCAD003:
    """TC-AD-003: CRITICAL severity when metric exceeds threshold by > 50%."""

    def test_critical_severity(self, detector):
        """CPU at 150 => excess=70, %excess=87.5% => CRITICAL."""
        metrics = {'cpu_usage': 150.0}
        anomalies = detector.detect_metric_anomalies(metrics)

        assert len(anomalies) == 1
        assert anomalies[0].severity == 'CRITICAL'
        print(f"[TC-AD-003] PASS  | severity=CRITICAL for cpu=150.0")


# ===================================================================
# TC-AD-004: Detect ERROR-level log anomaly
# ===================================================================

class TestTCAD004:
    """TC-AD-004: ERROR-level log entries produce LOG_ERROR anomalies."""

    def test_error_log_detection(self, detector):
        """ERROR-level log should create HIGH-severity anomaly."""
        logs = [{
            'level': 'ERROR',
            'message': 'Application crashed unexpectedly',
            'timestamp': '2026-04-26T10:00:00'
        }]
        anomalies = detector.detect_log_anomalies(logs)

        assert len(anomalies) == 1
        a = anomalies[0]
        assert a.anomaly_type == 'LOG_ERROR'
        assert a.severity == 'HIGH'
        print(f"[TC-AD-004] PASS  | type={a.anomaly_type}, severity={a.severity}")


# ===================================================================
# TC-AD-005: CRITICAL severity for deployment failure keywords
# ===================================================================

class TestTCAD005:
    """TC-AD-005: Deployment failure keywords escalate severity to CRITICAL."""

    def test_deployment_keyword_critical(self, detector):
        """ERROR log with 'deployment failed' => severity=CRITICAL."""
        logs = [{
            'level': 'ERROR',
            'message': 'Deployment failed - connection timeout',
            'timestamp': datetime.now()
        }]
        anomalies = detector.detect_log_anomalies(logs)

        assert len(anomalies) == 1
        assert anomalies[0].severity == 'CRITICAL'
        print("[TC-AD-005] PASS  | deployment keyword -> CRITICAL")


# ===================================================================
# TC-AD-006: No anomaly for INFO/DEBUG logs
# ===================================================================

class TestTCAD006:
    """TC-AD-006: Normal INFO/DEBUG logs without error keywords => 0 anomalies."""

    def test_info_debug_no_anomaly(self, detector):
        """INFO and DEBUG logs should not produce anomalies."""
        logs = [
            {'level': 'INFO', 'message': 'Application started successfully',
             'timestamp': datetime.now()},
            {'level': 'DEBUG', 'message': 'Loading configuration',
             'timestamp': datetime.now()},
        ]
        anomalies = detector.detect_log_anomalies(logs)

        assert len(anomalies) == 0
        print("[TC-AD-006] PASS  | 0 anomalies for INFO/DEBUG logs")


# ===================================================================
# TC-AD-007: Statistical anomaly detection
# ===================================================================

class TestTCAD007:
    """TC-AD-007: Statistical detection fires when value deviates beyond mean+2*stdev."""

    def test_statistical_anomaly(self, detector):
        """Feed 10 low CPU readings, then a high one within threshold but
        statistically anomalous."""
        # Build baseline: 10 readings around 40%
        baseline_values = [38.0, 39.0, 40.0, 41.0, 42.0,
                           39.5, 40.5, 38.5, 41.5, 40.0]
        for val in baseline_values:
            detector.detect_metric_anomalies({'cpu_usage': val})

        # Inject statistically anomalous value (within threshold of 80 but
        # well above mean~40 + 2*stdev~2.6 => upper_bound ~ 45.2)
        anomalies = detector.detect_metric_anomalies({'cpu_usage': 75.0})

        assert len(anomalies) >= 1, "Statistical anomaly should be detected"
        # Could be threshold-based OR statistical; either way it fires
        print(f"[TC-AD-007] PASS  | Statistical anomaly detected, "
              f"severity={anomalies[0].severity}")


# ===================================================================
# TC-AD-008: Empty input handling
# ===================================================================

class TestTCAD008:
    """TC-AD-008: Empty logs/metrics should return empty list, no exceptions."""

    def test_empty_logs(self, detector):
        """Empty logs list => empty anomaly list."""
        anomalies = detector.detect_log_anomalies([])
        assert anomalies == []
        print("[TC-AD-008a] PASS | empty logs => []")

    def test_empty_metrics(self, detector):
        """Empty metrics dict => empty anomaly list."""
        anomalies = detector.detect_metric_anomalies({})
        assert anomalies == []
        print("[TC-AD-008b] PASS | empty metrics => []")


# ===================================================================
# TC-AD-009: Invalid threshold raises ValueError
# ===================================================================

class TestTCAD009:
    """TC-AD-009: Non-dict threshold argument must raise ValueError."""

    def test_invalid_thresholds_string(self):
        """String thresholds should raise ValueError."""
        with pytest.raises(ValueError, match="Thresholds must be a dictionary"):
            AnomalyDetector("invalid")

    def test_invalid_thresholds_list(self):
        """List thresholds should raise ValueError."""
        with pytest.raises(ValueError, match="Thresholds must be a dictionary"):
            AnomalyDetector([1, 2, 3])

    def test_invalid_thresholds_none(self):
        """None thresholds should raise ValueError."""
        with pytest.raises(ValueError, match="Thresholds must be a dictionary"):
            AnomalyDetector(None)


# ===================================================================
# TC-AD-010: Boundary value at exact threshold
# ===================================================================

class TestTCAD010:
    """TC-AD-010: Value exactly at threshold max_value => no anomaly."""

    def test_exact_threshold(self, detector):
        """cpu_usage=80.0 is NOT > 80 => no anomaly."""
        metrics = {'cpu_usage': 80.0}
        anomalies = detector.detect_metric_anomalies(metrics)

        assert len(anomalies) == 0, (
            f"Expected 0 anomalies at boundary, got {len(anomalies)}"
        )
        print("[TC-AD-010] PASS  | boundary value 80.0 => no anomaly")

    def test_just_above_threshold(self, detector):
        """cpu_usage=80.01 IS > 80 => 1 anomaly."""
        # Need a fresh detector so baseline doesn't interfere
        thresholds = {'cpu_usage': Threshold(min_value=0, max_value=80)}
        det = AnomalyDetector(thresholds)

        metrics = {'cpu_usage': 80.01}
        anomalies = det.detect_metric_anomalies(metrics)

        assert len(anomalies) == 1
        print("[TC-AD-010b] PASS | 80.01 => 1 anomaly")


# ===================================================================
# Additional integration-style tests
# ===================================================================

class TestIntegrationAnomalyDetector:
    """Integration tests exercising multiple detector capabilities."""

    def test_mixed_logs_produce_correct_counts(self, detector):
        """Mix of ERROR, CRITICAL, INFO, WARNING logs with various keywords."""
        logs = [
            {'level': 'ERROR', 'message': 'Deployment failed - connection timeout',
             'timestamp': datetime.now()},
            {'level': 'INFO', 'message': 'Application started', 'timestamp': datetime.now()},
            {'level': 'CRITICAL', 'message': 'Out of memory', 'timestamp': datetime.now()},
            {'level': 'WARNING', 'message': 'High memory usage detected',
             'timestamp': datetime.now()},
            {'level': 'WARNING', 'message': 'Connection refused to database',
             'timestamp': datetime.now()},
        ]
        anomalies = detector.detect_log_anomalies(logs)

        # ERROR (deployment failed) -> 1 (CRITICAL)
        # CRITICAL (out of memory) -> 1 (CRITICAL)
        # WARNING (connection refused) -> 1 (DEPLOYMENT_ERROR / MEDIUM)
        assert len(anomalies) == 3, f"Expected 3 anomalies, got {len(anomalies)}"
        print(f"[Integration] PASS | mixed logs => {len(anomalies)} anomalies")

    def test_anomaly_history_accumulates(self, detector):
        """History should grow as anomalies are detected."""
        assert len(detector.get_anomaly_history()) == 0

        detector.detect_metric_anomalies({'cpu_usage': 95.0})
        assert len(detector.get_anomaly_history()) == 1

        detector.detect_log_anomalies([
            {'level': 'ERROR', 'message': 'fail', 'timestamp': datetime.now()}
        ])
        assert len(detector.get_anomaly_history()) == 2

        detector.clear_history()
        assert len(detector.get_anomaly_history()) == 0
        print("[Integration] PASS | anomaly history accumulation & clear")

    def test_to_dict_serialization(self, detector):
        """Anomaly.to_dict() should produce a JSON-serializable dictionary."""
        metrics = {'cpu_usage': 99.0}
        anomalies = detector.detect_metric_anomalies(metrics)
        d = anomalies[0].to_dict()

        assert isinstance(d, dict)
        assert 'id' in d
        assert 'type' in d
        assert 'severity' in d
        assert 'value' in d
        assert 'metric' in d
        assert 'timestamp' in d
        assert 'description' in d
        print(f"[Integration] PASS | to_dict keys: {list(d.keys())}")

    def test_is_anomaly_helper(self, detector):
        """is_anomaly() should return True/False correctly."""
        assert detector.is_anomaly(95.0, 'cpu_usage') is True
        assert detector.is_anomaly(50.0, 'cpu_usage') is False
        assert detector.is_anomaly(50.0, 'unknown_metric') is False
        print("[Integration] PASS | is_anomaly() helper works correctly")

    def test_set_threshold_updates(self, detector):
        """set_threshold() should allow updating thresholds at runtime."""
        assert detector.is_anomaly(90.0, 'cpu_usage') is True

        # Raise threshold
        detector.set_threshold('cpu_usage', Threshold(min_value=0, max_value=95))
        assert detector.is_anomaly(90.0, 'cpu_usage') is False
        assert detector.is_anomaly(96.0, 'cpu_usage') is True
        print("[Integration] PASS | set_threshold runtime update works")

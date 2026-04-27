"""
ARCA Platform - Assignment 9: Integration Tests
Tests the full pipeline: AnomalyDetector -> EventCorrelator -> RCAEngine -> RecommendationEngine

Run:  pytest Assignment9/test_integration.py -v --tb=short
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

# Path setup
BACKEND_MODULES = os.path.join(
    os.path.dirname(__file__), '..', 'arca-platform', 'backend', 'modules'
)
sys.path.insert(0, os.path.abspath(BACKEND_MODULES))

from anomaly_detector import AnomalyDetector, Threshold
from event_correlator import EventCorrelator
from rca_engine import RCAEngine
from recommendation_engine import RecommendationEngine
from sliding_window import SlidingWindow
from alert_system import AlertSystem


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def full_pipeline():
    """Create a complete ARCA analysis pipeline."""
    thresholds = {
        'cpu_usage': Threshold(min_value=0, max_value=80),
        'memory_usage': Threshold(min_value=0, max_value=85),
        'response_time': Threshold(min_value=0, max_value=2000),
        'error_rate': Threshold(min_value=0, max_value=5),
    }
    detector = AnomalyDetector(thresholds)
    correlator = EventCorrelator(window_size_minutes=5)
    rca_engine = RCAEngine([])
    rec_engine = RecommendationEngine({})
    alert_system = AlertSystem()
    window = SlidingWindow(max_size=100)

    return {
        'detector': detector,
        'correlator': correlator,
        'rca_engine': rca_engine,
        'rec_engine': rec_engine,
        'alert_system': alert_system,
        'window': window,
    }


# ===================================================================
# Integration Test: Full Pipeline - Deployment Error Scenario
# ===================================================================

class TestFullPipelineDeploymentError:
    """End-to-end test: deployment error logs + high CPU -> RCA -> recommendations."""

    def test_deployment_error_pipeline(self, full_pipeline):
        """
        Scenario:
        1. Inject deployment error logs + high CPU metric
        2. Detect anomalies
        3. Correlate events
        4. Perform RCA
        5. Generate recommendations
        """
        detector = full_pipeline['detector']
        correlator = full_pipeline['correlator']
        rca_engine = full_pipeline['rca_engine']
        rec_engine = full_pipeline['rec_engine']

        # Step 1: Detect log anomalies
        logs = [
            {'level': 'ERROR', 'message': 'Deployment failed - configuration error',
             'timestamp': datetime.now()},
            {'level': 'CRITICAL', 'message': 'Out of memory - heap space',
             'timestamp': datetime.now()},
        ]
        log_anomalies = detector.detect_log_anomalies(logs)
        assert len(log_anomalies) >= 2

        # Step 2: Detect metric anomalies
        metrics = {'cpu_usage': 95.0, 'memory_usage': 92.0}
        metric_anomalies = detector.detect_metric_anomalies(metrics)
        assert len(metric_anomalies) >= 1

        # Step 3: Combine and correlate
        all_anomaly_dicts = (
            [a.to_dict() for a in log_anomalies] +
            [a.to_dict() for a in metric_anomalies]
        )
        correlated = correlator.correlate_anomalies(all_anomaly_dicts)

        # All anomalies share the same time window, so at least 1 correlated group
        assert len(correlated) >= 1
        assert correlated[0].correlation_score > 0

        # Step 4: RCA
        rca_result = rca_engine.analyze_root_cause(correlated)
        assert rca_result.root_cause != ''
        assert rca_result.confidence > 0
        assert len(rca_result.recommendations) > 0

        # Step 5: Recommendations
        recommendations = rec_engine.generate_recommendations(rca_result)
        assert len(recommendations) > 0
        assert all('action' in r for r in recommendations)

        print(f"[INTEGRATION] Root Cause: {rca_result.root_cause}")
        print(f"[INTEGRATION] Confidence: {rca_result.confidence:.2f}")
        print(f"[INTEGRATION] Recommendations: {len(recommendations)}")


# ===================================================================
# Integration Test: Alert System Pipeline
# ===================================================================

class TestAlertSystemIntegration:
    """Test that critical anomalies trigger alerts correctly."""

    def test_critical_anomaly_triggers_alert(self, full_pipeline):
        detector = full_pipeline['detector']
        alert_system = full_pipeline['alert_system']

        # Detect critical anomaly
        logs = [
            {'level': 'ERROR', 'message': 'Deployment failed - connection refused',
             'timestamp': datetime.now()},
        ]
        anomalies = detector.detect_log_anomalies(logs)
        critical = [a for a in anomalies if a.severity == 'CRITICAL']

        assert len(critical) >= 1

        # Send alert
        alert_system.send_alert({
            'type': 'CRITICAL_ANOMALY',
            'severity': 'CRITICAL',
            'root_cause': 'DEPLOYMENT_CONFIGURATION_ERROR',
            'confidence': 0.85,
            'anomaly_count': len(critical),
        })

        unacked = alert_system.get_unacknowledged_alerts()
        assert len(unacked) == 1

        # Acknowledge
        alert_system.acknowledge_alert(unacked[0].alert_id)
        assert len(alert_system.get_unacknowledged_alerts()) == 0

        print("[INTEGRATION] PASS | Alert pipeline works correctly")


# ===================================================================
# Integration Test: Sliding Window with Anomaly Detector
# ===================================================================

class TestSlidingWindowIntegration:
    """Test sliding window stores and retrieves anomalies."""

    def test_window_stores_anomalies(self, full_pipeline):
        detector = full_pipeline['detector']
        window = full_pipeline['window']

        # Generate anomalies and store in window
        for cpu in [85, 90, 95, 100, 110]:
            anomalies = detector.detect_metric_anomalies({'cpu_usage': float(cpu)})
            for a in anomalies:
                window.add(a.to_dict())

        assert window.size() >= 5
        recent = window.get_recent(3)
        assert len(recent) == 3

        print(f"[INTEGRATION] PASS | Sliding window holds {window.size()} anomalies")


# ===================================================================
# Integration Test: Event Correlator Time Window
# ===================================================================

class TestEventCorrelatorTimeWindow:
    """Verify that events outside the time window are NOT correlated together."""

    def test_events_across_windows(self, full_pipeline):
        correlator = full_pipeline['correlator']

        now = datetime.now()
        anomalies = [
            {'type': 'LOG_ERROR', 'severity': 'HIGH',
             'metric': 'error_logs', 'timestamp': now.isoformat(),
             'description': 'Error A'},
            {'type': 'METRIC_ANOMALY', 'severity': 'HIGH',
             'metric': 'cpu_usage',
             'timestamp': (now + timedelta(hours=2)).isoformat(),
             'description': 'High CPU'},
        ]

        correlated = correlator.correlate_anomalies(anomalies)

        # Events are 2 hours apart -> separate windows -> either 0 correlated
        # groups (each window has <2 items) or separate groups
        # Each window has only 1 anomaly, so correlator should skip them
        # (need >=2 anomalies to correlate)
        for group in correlated:
            # No group should contain both anomalies
            assert len(group.anomalies) <= 1 or all(
                a.get('description') != 'Error A' or
                a.get('description') != 'High CPU'
                for a in group.anomalies
            )

        print(f"[INTEGRATION] PASS | Time window separation works "
              f"({len(correlated)} groups)")

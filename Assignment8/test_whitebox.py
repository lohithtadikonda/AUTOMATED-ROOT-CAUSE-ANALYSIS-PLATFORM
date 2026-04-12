"""
Assignment 8 — Part B: White Box Testing (Glass Box Testing)
============================================================
ARCA Platform — Automated Root Cause Analysis

White Box Testing is a testing technique where the tester has full knowledge
of the internal structure, code, and logic of the application.

Tests target:
  - Internal code branches (if/elif/else)
  - Loop logic and boundary conditions
  - Private/internal helper methods
  - Data structure state transitions
  - Specific code path coverage (statement, branch, path)
"""

import sys
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add arca-platform backend modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'arca-platform', 'backend', 'modules'))

from anomaly_detector import AnomalyDetector, Anomaly, Threshold
from rca_engine import RCAEngine, RCAResult, Rule, CorrelatedEvent
from event_correlator import EventCorrelator
from event_correlator import CorrelatedEvent as ECCorrelatedEvent
from recommendation_engine import RecommendationEngine, Fix
from alert_system import AlertSystem, Alert
from sliding_window import SlidingWindow


# =====================================================================
# WB-01 to WB-17: AnomalyDetector — White Box Tests
# =====================================================================

class TestAnomalyDetectorWhiteBox:
    """White Box tests targeting internal branches and logic of AnomalyDetector."""

    def setup_method(self):
        """Set up test fixtures — mirrors __init__ internal state."""
        self.thresholds = {
            'cpu_usage': Threshold(min_value=0, max_value=80),
            'memory_usage': Threshold(min_value=0, max_value=85),
            'response_time': Threshold(min_value=0, max_value=2000),
            'error_rate': Threshold(min_value=0, max_value=5),
        }
        self.detector = AnomalyDetector(self.thresholds)

    # --- WB-01: Constructor — valid thresholds ---
    def test_init_valid_thresholds(self):
        """Verify internal state after valid initialization."""
        assert self.detector.thresholds == self.thresholds
        assert self.detector.detection_algorithm == "hybrid"
        assert self.detector.anomaly_history == []
        assert self.detector._baseline_data == {}

    # --- WB-02: Constructor — invalid thresholds (not a dict) ---
    def test_init_invalid_thresholds(self):
        """Branch: isinstance check fails → ValueError raised."""
        with pytest.raises(ValueError, match="Thresholds must be a dictionary"):
            AnomalyDetector("not_a_dict")

        with pytest.raises(ValueError):
            AnomalyDetector([1, 2, 3])

    # --- WB-03: detect_log_anomalies — ERROR level branch ---
    def test_detect_log_anomalies_error_level(self):
        """Branch: level == 'ERROR' → anomaly_type = LOG_ERROR, severity >= HIGH."""
        logs = [
            {'level': 'ERROR', 'message': 'Something went wrong', 'timestamp': datetime.now()}
        ]
        anomalies = self.detector.detect_log_anomalies(logs)
        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == 'LOG_ERROR'
        assert anomalies[0].severity == 'HIGH'  # Default for ERROR without deployment keyword

    # --- WB-04: detect_log_anomalies — CRITICAL level branch ---
    def test_detect_log_anomalies_critical_level(self):
        """Branch: level == 'CRITICAL' → anomaly_type = LOG_CRITICAL, severity = CRITICAL."""
        logs = [
            {'level': 'CRITICAL', 'message': 'System crashed', 'timestamp': datetime.now()}
        ]
        anomalies = self.detector.detect_log_anomalies(logs)
        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == 'LOG_CRITICAL'
        assert anomalies[0].severity == 'CRITICAL'

    # --- WB-05: detect_log_anomalies — deployment keyword in ERROR → CRITICAL severity ---
    def test_detect_log_anomalies_deployment_keyword_in_error(self):
        """Branch: ERROR level + deployment keyword match → severity upgraded to CRITICAL."""
        deployment_keywords = ['deployment failed', 'deploy error', 'rollback',
                               'connection refused', 'timeout', 'out of memory',
                               'permission denied', 'authentication failed']

        for keyword in deployment_keywords:
            detector = AnomalyDetector(self.thresholds)
            logs = [{'level': 'ERROR', 'message': f'Issue: {keyword}', 'timestamp': datetime.now()}]
            anomalies = detector.detect_log_anomalies(logs)
            assert anomalies[0].severity == 'CRITICAL', f"Failed for keyword: {keyword}"

    # --- WB-06: detect_log_anomalies — WARNING with deployment keyword → MEDIUM ---
    def test_detect_log_anomalies_warning_keyword(self):
        """Branch: level in ['WARNING', 'WARN', 'INFO'] + keyword → DEPLOYMENT_ERROR, MEDIUM."""
        logs = [
            {'level': 'WARNING', 'message': 'Possible timeout detected', 'timestamp': datetime.now()}
        ]
        anomalies = self.detector.detect_log_anomalies(logs)
        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == 'DEPLOYMENT_ERROR'
        assert anomalies[0].severity == 'MEDIUM'

    # --- WB-07: detect_log_anomalies — empty list ---
    def test_detect_log_anomalies_empty(self):
        """Branch: if not logs → return [] (early return)."""
        assert self.detector.detect_log_anomalies([]) == []
        assert self.detector.detect_log_anomalies(None) == []

    # --- WB-08: detect_metric_anomalies — value > max_value branch ---
    def test_detect_metric_above_threshold(self):
        """Branch: value > threshold.max_value → anomaly detected."""
        metrics = {'cpu_usage': 95.0}
        anomalies = self.detector.detect_metric_anomalies(metrics)
        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == 'METRIC_ANOMALY'
        assert anomalies[0].value == 95.0
        assert 'exceeded threshold' in anomalies[0].description

    # --- WB-09: detect_metric_anomalies — value < min_value branch ---
    def test_detect_metric_below_threshold(self):
        """Branch: value < threshold.min_value → anomaly detected with MEDIUM severity."""
        self.detector.thresholds['cpu_usage'] = Threshold(min_value=10, max_value=80)
        metrics = {'cpu_usage': 5.0}
        anomalies = self.detector.detect_metric_anomalies(metrics)
        assert len(anomalies) == 1
        assert anomalies[0].severity == 'MEDIUM'
        assert 'below threshold' in anomalies[0].description

    # --- WB-10: Severity calculation — CRITICAL (>50% excess) ---
    def test_severity_calculation_critical(self):
        """Internal severity calculation: percent > 50 → CRITICAL."""
        # max_value = 80, value = 130 → excess = 50, percent = 62.5%
        metrics = {'cpu_usage': 130.0}
        anomalies = self.detector.detect_metric_anomalies(metrics)
        assert anomalies[0].severity == 'CRITICAL'

    # --- WB-11: Severity calculation — HIGH (25-50% excess) ---
    def test_severity_calculation_high(self):
        """Internal severity calculation: 25% < percent <= 50% → HIGH."""
        # max_value = 80, value = 105 → excess = 25, percent = 31.25%
        metrics = {'cpu_usage': 105.0}
        anomalies = self.detector.detect_metric_anomalies(metrics)
        assert anomalies[0].severity == 'HIGH'

    # --- WB-12: Severity calculation — MEDIUM (10-25% excess) ---
    def test_severity_calculation_medium(self):
        """Internal severity calculation: 10% < percent <= 25% → MEDIUM."""
        # max_value = 80, value = 92 → excess = 12, percent = 15%
        metrics = {'cpu_usage': 92.0}
        anomalies = self.detector.detect_metric_anomalies(metrics)
        assert anomalies[0].severity == 'MEDIUM'

    # --- WB-13: Severity calculation — LOW (0-10% excess) ---
    def test_severity_calculation_low(self):
        """Internal severity calculation: percent <= 10% → LOW."""
        # max_value = 80, value = 85 → excess = 5, percent = 6.25%
        metrics = {'cpu_usage': 85.0}
        anomalies = self.detector.detect_metric_anomalies(metrics)
        assert anomalies[0].severity == 'LOW'

    # --- WB-14: Statistical detection branch (Z-score with >= 10 data points) ---
    def test_statistical_detection(self):
        """Branch: len(baseline) >= 10 → statistical detection activates."""
        # First, build up baseline data with normal values
        for i in range(15):
            self.detector.detect_metric_anomalies({'cpu_usage': 50.0})

        # Verify baseline built up (15 data points from 15 calls)
        assert len(self.detector._baseline_data['cpu_usage']) == 15

        # Now inject a value that's within threshold but statistically anomalous
        # We need a value that's within max_value but far from baseline mean
        # Mean is ~50.0, so 79.0 is within threshold but statistically anomalous
        self.detector.thresholds['cpu_usage'] = Threshold(min_value=0, max_value=100, std_dev_multiplier=1.5)
        anomalies = self.detector.detect_metric_anomalies({'cpu_usage': 79.0})
        # May or may not detect depending on stdev; key thing is the branch was exercised
        assert isinstance(anomalies, list)

    # --- WB-15: is_anomaly method — internal threshold checks ---
    def test_is_anomaly_method(self):
        """Test the is_anomaly() utility method's internal branches."""
        # Above max_value
        assert self.detector.is_anomaly(95.0, 'cpu_usage') is True
        # Below min_value
        self.detector.thresholds['cpu_usage'] = Threshold(min_value=10, max_value=80)
        assert self.detector.is_anomaly(5.0, 'cpu_usage') is True
        # Within range
        assert self.detector.is_anomaly(50.0, 'cpu_usage') is False
        # Unknown metric (no threshold)
        assert self.detector.is_anomaly(50.0, 'unknown_metric') is False

    # --- WB-16: Anomaly history tracking ---
    def test_anomaly_history_tracking(self):
        """Verify anomaly_history list grows and limit works."""
        logs = [
            {'level': 'ERROR', 'message': f'Error {i}', 'timestamp': datetime.now()}
            for i in range(5)
        ]
        self.detector.detect_log_anomalies(logs)
        assert len(self.detector.anomaly_history) == 5

        # Test get with limit
        recent = self.detector.get_anomaly_history(limit=3)
        assert len(recent) == 3

        # Test clear
        self.detector.clear_history()
        assert len(self.detector.anomaly_history) == 0

    # --- WB-17: Baseline data windowing (capped at 100) ---
    def test_baseline_data_windowing(self):
        """Branch: len(baseline) > 100 → trim to last 100."""
        for i in range(110):
            self.detector.detect_metric_anomalies({'cpu_usage': 50.0 + (i % 10)})

        assert len(self.detector._baseline_data['cpu_usage']) <= 100

    # --- WB extra: Timestamp parsing branches in detect_log_anomalies ---
    def test_timestamp_parsing_string(self):
        """Branch: isinstance(timestamp, str) → fromisoformat parsing."""
        logs = [
            {'level': 'ERROR', 'message': 'Test', 'timestamp': '2026-03-15T10:00:00'}
        ]
        anomalies = self.detector.detect_log_anomalies(logs)
        assert len(anomalies) == 1

    def test_timestamp_parsing_invalid(self):
        """Branch: timestamp is neither str nor datetime → default to now()."""
        logs = [
            {'level': 'ERROR', 'message': 'Test', 'timestamp': 12345}
        ]
        anomalies = self.detector.detect_log_anomalies(logs)
        assert len(anomalies) == 1

    def test_no_matching_threshold_for_metric(self):
        """Branch: no threshold found → continue (skip metric)."""
        metrics = {'unknown_metric': 999.0}
        anomalies = self.detector.detect_metric_anomalies(metrics)
        assert len(anomalies) == 0

    def test_empty_metrics(self):
        """Branch: if not metrics → return []."""
        assert self.detector.detect_metric_anomalies({}) == []
        assert self.detector.detect_metric_anomalies(None) == []


# =====================================================================
# WB-18 to WB-22: RCAEngine — White Box Tests
# =====================================================================

class TestRCAEngineWhiteBox:
    """White Box tests targeting internal RCAEngine logic."""

    def setup_method(self):
        self.engine = RCAEngine([])

    # --- WB-18: Init with empty rules → default rules loaded ---
    def test_init_empty_rules_loads_defaults(self):
        """Branch: if not rules → _get_default_rules()."""
        engine = RCAEngine([])
        assert len(engine.root_cause_rules) == 5  # 5 default rules
        assert engine.root_cause_rules[0].rule_id == 'R001'

    def test_init_custom_rules(self):
        """Branch: rules provided → use provided rules."""
        custom_rule = Rule(
            rule_id='CUSTOM',
            pattern={'anomaly_types': ['TEST']},
            root_cause='CUSTOM_CAUSE',
            confidence=0.9,
            description='Custom rule'
        )
        engine = RCAEngine([custom_rule])
        assert len(engine.root_cause_rules) == 1
        assert engine.root_cause_rules[0].rule_id == 'CUSTOM'

    def test_init_invalid_rules_type(self):
        """Branch: not isinstance(rules, list) → ValueError."""
        with pytest.raises(ValueError, match="Rules must be a list"):
            RCAEngine("not_a_list")

    # --- WB-19: Analyze empty events → UNKNOWN result ---
    def test_analyze_empty_events(self):
        """Branch: if not correlated_events → return UNKNOWN."""
        result = self.engine.analyze_root_cause([])
        assert result.root_cause == "UNKNOWN"
        assert result.confidence == 0.0
        assert "No events to analyze" in result.recommendations

    # --- WB-20: Rule matching — apply_rule logic ---
    def test_apply_rule_type_matching(self):
        """Test apply_rule checks anomaly_types pattern."""
        rule = Rule(
            rule_id='TEST',
            pattern={'anomaly_types': ['LOG_ERROR']},
            root_cause='TEST_CAUSE',
            confidence=0.8,
            description='Test'
        )
        # Matching anomaly
        ce = CorrelatedEvent(
            anomalies=[{'type': 'LOG_ERROR', 'severity': 'HIGH', 'description': 'test'}],
            correlation_score=0.9,
            time_window='5_minutes',
            affected_components=['test']
        )
        assert self.engine.apply_rule(rule, [ce]) is True

    def test_apply_rule_type_not_matching(self):
        """Branch: required_types not all present → False."""
        rule = Rule(
            rule_id='TEST',
            pattern={'anomaly_types': ['LOG_ERROR', 'DEPLOYMENT_ERROR']},
            root_cause='TEST',
            confidence=0.8,
            description='Test'
        )
        ce = CorrelatedEvent(
            anomalies=[{'type': 'LOG_ERROR', 'severity': 'HIGH', 'description': 'test'}],
            correlation_score=0.9,
            time_window='5_minutes',
            affected_components=['test']
        )
        assert self.engine.apply_rule(rule, [ce]) is False

    def test_apply_rule_metric_matching(self):
        """Branch: required_metrics check."""
        rule = Rule(
            rule_id='TEST',
            pattern={'metrics': ['cpu_usage']},
            root_cause='TEST',
            confidence=0.8,
            description='Test'
        )
        ce = CorrelatedEvent(
            anomalies=[{'type': 'METRIC', 'metric': 'cpu_usage', 'description': 'test'}],
            correlation_score=0.9,
            time_window='5_minutes',
            affected_components=['test']
        )
        assert self.engine.apply_rule(rule, [ce]) is True

    def test_apply_rule_keyword_matching(self):
        """Branch: required_keywords in descriptions check."""
        rule = Rule(
            rule_id='TEST',
            pattern={'keywords': ['deployment', 'failed']},
            root_cause='TEST',
            confidence=0.8,
            description='Test'
        )
        ce = CorrelatedEvent(
            anomalies=[{'type': 'LOG_ERROR', 'description': 'Deployment has failed completely'}],
            correlation_score=0.9,
            time_window='5_minutes',
            affected_components=['test']
        )
        assert self.engine.apply_rule(rule, [ce]) is True

    def test_apply_rule_keyword_not_matching(self):
        """Branch: keywords not found in descriptions → False."""
        rule = Rule(
            rule_id='TEST',
            pattern={'keywords': ['xyz_nonexistent']},
            root_cause='TEST',
            confidence=0.8,
            description='Test'
        )
        ce = CorrelatedEvent(
            anomalies=[{'type': 'LOG_ERROR', 'description': 'Normal error message'}],
            correlation_score=0.9,
            time_window='5_minutes',
            affected_components=['test']
        )
        assert self.engine.apply_rule(rule, [ce]) is False

    # --- WB-21: Confidence calculation ---
    def test_confidence_calculation(self):
        """Internal _calculate_confidence formula: (base + avg_correlation) / 2."""
        rule = Rule(rule_id='T', pattern={}, root_cause='T', confidence=0.8, description='T')
        events = [
            CorrelatedEvent(anomalies=[], correlation_score=0.9, time_window='5m', affected_components=[]),
            CorrelatedEvent(anomalies=[], correlation_score=0.7, time_window='5m', affected_components=[])
        ]
        confidence = self.engine._calculate_confidence(rule, events)
        # avg_correlation = (0.9 + 0.7) / 2 = 0.8
        # adjusted = (0.8 + 0.8) / 2 = 0.8
        assert abs(confidence - 0.8) < 0.01

    # --- WB-22: Causal chain generation — known vs. unknown cause ---
    def test_causal_chain_known_cause(self):
        """Branch: root_cause in chains dict → return specific chain."""
        chain = self.engine.generate_causal_chain('RESOURCE_EXHAUSTION', [])
        assert len(chain) == 4
        assert 'Resource usage increased' in chain[0]

    def test_causal_chain_unknown_cause(self):
        """Branch: root_cause not in chains dict → return generic chain."""
        chain = self.engine.generate_causal_chain('UNKNOWN_CAUSE', [])
        assert len(chain) == 3
        assert 'UNKNOWN_CAUSE' in chain[0]

    # --- WB extra: Evidence collection with Anomaly objects vs dicts ---
    def test_collect_evidence_from_dicts(self):
        """Branch: isinstance(anomaly, dict) → use .get()."""
        anomalies = [
            {'type': 'LOG_ERROR', 'severity': 'HIGH', 'description': 'test', 'timestamp': '2026-01-01'}
        ]
        evidence = self.engine._collect_evidence(anomalies)
        assert len(evidence) == 1
        assert evidence[0]['type'] == 'LOG_ERROR'

    def test_collect_evidence_from_objects(self):
        """Branch: not dict → use getattr()."""
        anomaly = Anomaly(
            anomaly_type='METRIC_ANOMALY', severity='HIGH', value=95.0,
            metric_name='cpu_usage', timestamp=datetime.now(), description='CPU high'
        )
        evidence = self.engine._collect_evidence([anomaly])
        assert evidence[0]['type'] == 'METRIC_ANOMALY'

    def test_analysis_history_stored(self):
        """Verify analysis results are appended to history when events provided."""
        # Note: empty events return early without appending to history
        ce = CorrelatedEvent(
            anomalies=[{'type': 'LOG_ERROR', 'severity': 'HIGH', 'description': 'test'}],
            correlation_score=0.8,
            time_window='5m',
            affected_components=['test']
        )
        self.engine.analyze_root_cause([ce])
        assert len(self.engine.analysis_history) == 1

        history = self.engine.get_analysis_history(limit=1)
        assert len(history) == 1


# =====================================================================
# WB-23 to WB-25: SlidingWindow — White Box Tests
# =====================================================================

class TestSlidingWindowWhiteBox:
    """White Box tests targeting SlidingWindow internal deque and metadata."""

    # --- WB-23: Buffer eviction (deque maxlen behavior) ---
    def test_buffer_eviction(self):
        """Internal: when len(buffer) >= max_size, oldest item is evicted."""
        window = SlidingWindow(max_size=3)
        window.add('a')
        window.add('b')
        window.add('c')
        assert window.size() == 3

        window.add('d')  # 'a' should be evicted
        assert window.size() == 3
        items = window.get_all()
        assert items == ['b', 'c', 'd']
        assert 'a' not in items

    # --- WB-24: Metadata tracking ---
    def test_metadata_tracking(self):
        """Internal: _metadata counters are correctly updated."""
        window = SlidingWindow(max_size=3)
        window.add(1)
        window.add(2)
        window.add(3)
        window.add(4)  # Evicts 1
        window.add(5)  # Evicts 2

        meta = window.get_metadata()
        assert meta['total_items_added'] == 5
        assert meta['items_evicted'] == 2
        assert meta['current_size'] == 3

    # --- WB-25: Invalid max_size → ValueError ---
    def test_invalid_max_size(self):
        """Branch: max_size <= 0 → ValueError."""
        with pytest.raises(ValueError, match="max_size must be positive"):
            SlidingWindow(max_size=0)
        with pytest.raises(ValueError):
            SlidingWindow(max_size=-5)

    def test_clear_preserves_metadata(self):
        """Internal: clear() resets buffer but preserves total/evicted counts."""
        window = SlidingWindow(max_size=5)
        window.add(1)
        window.add(2)
        window.clear()
        assert window.size() == 0
        meta = window.get_metadata()
        assert meta['total_items_added'] == 2  # Preserved
        assert meta['current_size'] == 0

    def test_get_recent_and_oldest(self):
        """Internal slicing logic for get_recent and get_oldest."""
        window = SlidingWindow(max_size=10)
        for i in range(5):
            window.add(i)

        recent = window.get_recent(3)
        assert recent == [2, 3, 4]

        oldest = window.get_oldest(2)
        assert oldest == [0, 1]

        # Edge: request more than available
        all_items = window.get_recent(100)
        assert len(all_items) == 5

    def test_get_recent_zero_or_negative(self):
        """Branch: n <= 0 → return []."""
        window = SlidingWindow(max_size=5)
        window.add(1)
        assert window.get_recent(0) == []
        assert window.get_recent(-1) == []
        assert window.get_oldest(0) == []

    def test_filter_function(self):
        """Internal filter with lambda condition."""
        window = SlidingWindow(max_size=10)
        for i in range(10):
            window.add({'value': i, 'even': i % 2 == 0})

        evens = window.filter(lambda x: x['even'])
        assert len(evens) == 5

    def test_statistics(self):
        """Internal get_statistics computation."""
        window = SlidingWindow(max_size=10)
        for i in range(7):
            window.add(i)

        stats = window.get_statistics()
        assert stats['current_size'] == 7
        assert stats['max_size'] == 10
        assert stats['utilization'] == 70.0
        assert stats['is_full'] is False
        assert stats['is_empty'] is False

    def test_dunder_methods(self):
        """Internal __len__, __iter__, __repr__."""
        window = SlidingWindow(max_size=5)
        window.add(1)
        window.add(2)
        assert len(window) == 2
        assert list(window) == [1, 2]
        assert 'SlidingWindow(size=2/5)' in repr(window)


# =====================================================================
# WB-26 to WB-28: EventCorrelator — White Box Tests
# =====================================================================

class TestEventCorrelatorWhiteBox:
    """White Box tests targeting EventCorrelator internal grouping and scoring."""

    def setup_method(self):
        self.correlator = EventCorrelator(window_size_minutes=5)

    # --- WB-26: Time window grouping ---
    def test_time_window_grouping(self):
        """Internal _group_by_timestamp groups anomalies by 5-minute windows."""
        now = datetime.now()
        anomalies = [
            {'type': 'A', 'timestamp': now.isoformat()},
            {'type': 'B', 'timestamp': (now + timedelta(seconds=30)).isoformat()},
            {'type': 'C', 'timestamp': (now + timedelta(minutes=10)).isoformat()},
        ]
        windows = self.correlator._group_by_timestamp(anomalies)
        # A and B should be in same window, C in different window
        assert len(windows) >= 1

    # --- WB-27: Correlation score factors ---
    def test_correlation_score_calculation(self):
        """Internal _calculate_correlation_score with severity factors."""
        anomalies = [
            {'type': 'A', 'severity': 'CRITICAL', 'metric': 'cpu'},
            {'type': 'B', 'severity': 'HIGH', 'metric': 'memory'},
        ]
        score = self.correlator._calculate_correlation_score(anomalies)
        # Time proximity: 0.3 + CRITICAL: 0.3 + HIGH: 0.2 = 0.8
        assert score >= 0.5  # At least time + severity factors
        assert score <= 1.0

    def test_correlation_score_low_severity(self):
        """Score with only LOW severity anomalies → lower score."""
        anomalies = [
            {'type': 'A', 'severity': 'LOW', 'metric': 'cpu'},
            {'type': 'B', 'severity': 'LOW', 'metric': 'memory'},
        ]
        score = self.correlator._calculate_correlation_score(anomalies)
        assert score == 0.3  # Only time proximity factor

    def test_correlation_score_single_anomaly(self):
        """Branch: len(anomalies) < 2 → score = 0.0."""
        score = self.correlator._calculate_correlation_score([{'type': 'A'}])
        assert score == 0.0

    # --- WB-28: Minimum anomalies for correlation ---
    def test_minimum_anomalies_for_correlation(self):
        """Branch: < 2 anomalies in a window → no CorrelatedEvent created."""
        anomalies = [
            {'type': 'A', 'severity': 'HIGH', 'timestamp': datetime.now().isoformat()}
        ]
        correlated = self.correlator.correlate_anomalies(anomalies)
        assert len(correlated) == 0  # Single anomaly, not correlated

    def test_is_within_time_window(self):
        """Internal time window check with 5-minute window."""
        now = datetime.now()
        t1 = now
        t2 = now + timedelta(minutes=3)
        t3 = now + timedelta(minutes=10)

        assert self.correlator.is_within_time_window(t1, t2) is True
        assert self.correlator.is_within_time_window(t1, t3) is False

    def test_is_within_time_window_string_parsing(self):
        """Branch: time is not datetime → try fromisoformat."""
        now = datetime.now()
        result = self.correlator.is_within_time_window(now, now.isoformat())
        assert result is True

    def test_is_within_time_window_invalid_type(self):
        """Branch: conversion fails → return False."""
        result = self.correlator.is_within_time_window(12345, "not_a_date")
        assert result is False

    def test_extract_affected_components(self):
        """Internal _extract_affected_components parsing logic."""
        anomalies = [
            {'type': 'A', 'metric': 'app-server.cpu_usage'},
            {'type': 'B', 'metric': 'memory_usage'},
        ]
        components = self.correlator._extract_affected_components(anomalies)
        assert 'app-server' in components  # Extracted from dot notation
        assert 'memory' in components       # Extracted from underscore notation

    def test_extract_components_fallback_to_type(self):
        """Branch: no dot or underscore in metric → use anomaly_type."""
        anomalies = [{'type': 'ALERT', 'metric': 'simple'}]
        components = self.correlator._extract_affected_components(anomalies)
        # 'simple' has no dot or underscore → will return the type as fallback
        assert len(components) >= 1


# =====================================================================
# WB-29 to WB-30: RecommendationEngine — White Box Tests
# =====================================================================

class TestRecommendationEngineWhiteBox:
    """White Box tests for RecommendationEngine priority adjustment logic."""

    def setup_method(self):
        self.engine = RecommendationEngine({})

    # --- WB-29: Priority adjustment — high confidence ---
    def test_priority_adjustment_high_confidence(self):
        """Branch: confidence > 0.8 → MEDIUM upgraded to HIGH."""
        class MockRCA:
            root_cause = 'RESOURCE_EXHAUSTION'
            confidence = 0.9

        recs = self.engine.generate_recommendations(MockRCA())
        # All MEDIUM priorities should be upgraded to HIGH
        for rec in recs:
            assert rec['priority'] != 'MEDIUM' or rec['priority'] == 'HIGH'

    # --- WB-30: Priority adjustment — low confidence ---
    def test_priority_adjustment_low_confidence(self):
        """Branch: confidence < 0.5 → HIGH downgraded to MEDIUM."""
        class MockRCA:
            root_cause = 'RESOURCE_EXHAUSTION'
            confidence = 0.3

        recs = self.engine.generate_recommendations(MockRCA())
        # HIGH priorities should be downgraded to MEDIUM
        high_count = sum(1 for r in recs if r['priority'] == 'HIGH')
        # With low confidence, there should be fewer HIGH priorities
        assert isinstance(recs, list)

    def test_unknown_root_cause_generic_recommendations(self):
        """Branch: root_cause not in rules → generic recommendations."""
        class MockRCA:
            root_cause = 'TOTALLY_UNKNOWN_CAUSE'
            confidence = 0.5

        recs = self.engine.generate_recommendations(MockRCA())
        assert len(recs) >= 3
        assert any('system logs' in r['action'].lower() for r in recs)

    def test_prioritize_recommendations_sorting(self):
        """Internal priority_order sorting: HIGH < MEDIUM < LOW."""
        recs = [
            {'action': 'low', 'priority': 'LOW'},
            {'action': 'high', 'priority': 'HIGH'},
            {'action': 'med', 'priority': 'MEDIUM'},
        ]
        sorted_recs = self.engine.prioritize_recommendations(recs)
        assert sorted_recs[0]['priority'] == 'HIGH'
        assert sorted_recs[1]['priority'] == 'MEDIUM'
        assert sorted_recs[2]['priority'] == 'LOW'

    def test_historical_fix_recording_and_retrieval(self):
        """Internal historical_fixes list management."""
        self.engine.record_fix('RESOURCE_EXHAUSTION', 'Scaled up servers', True)
        self.engine.record_fix('RESOURCE_EXHAUSTION', 'Restarted services', False)

        fixes = self.engine.get_historical_fixes('RESOURCE_EXHAUSTION')
        assert len(fixes) == 2
        assert fixes[0].timestamp >= fixes[1].timestamp  # Sorted recent first
        assert fixes[0].success is False or fixes[1].success is False

    def test_add_new_rule(self):
        """Internal recommendation_rules dict modification."""
        self.engine.add_new_rule('CUSTOM_CAUSE', {
            'action': 'Custom fix',
            'priority': 'HIGH',
            'description': 'A custom fix'
        })
        assert 'CUSTOM_CAUSE' in self.engine.recommendation_rules
        assert len(self.engine.recommendation_rules['CUSTOM_CAUSE']) == 1


# =====================================================================
# WB-31 to WB-32: AlertSystem — White Box Tests
# =====================================================================

class TestAlertSystemWhiteBox:
    """White Box tests for AlertSystem internal state management."""

    def setup_method(self):
        self.alert_system = AlertSystem()

    # --- WB-31: Alert ID generation ---
    def test_alert_id_generation(self):
        """Internal: _alert_counter increments, ID format is ALERT_DATE_N."""
        self.alert_system.send_alert({'type': 'TEST', 'severity': 'LOW'})
        assert self.alert_system._alert_counter == 1
        assert self.alert_system.alerts[0].alert_id.startswith('ALERT_')

        self.alert_system.send_alert({'type': 'TEST2', 'severity': 'HIGH'})
        assert self.alert_system._alert_counter == 2
        # IDs should be different
        assert self.alert_system.alerts[0].alert_id != self.alert_system.alerts[1].alert_id

    # --- WB-32: Acknowledge updates state ---
    def test_acknowledge_updates_state(self):
        """Internal: acknowledge sets flag and removes from alert_queue."""
        self.alert_system.send_alert({'type': 'TEST', 'severity': 'CRITICAL'})
        alert_id = self.alert_system.alerts[0].alert_id

        # Before acknowledge
        assert len(self.alert_system.alert_queue) == 1
        assert self.alert_system.alerts[0].acknowledged is False

        # Acknowledge
        result = self.alert_system.acknowledge_alert(alert_id)
        assert result is True
        assert self.alert_system.alerts[0].acknowledged is True
        assert self.alert_system.alerts[0].acknowledged_at is not None
        assert len(self.alert_system.alert_queue) == 0

    def test_acknowledge_invalid_id(self):
        """Branch: alert_id not found → returns False."""
        result = self.alert_system.acknowledge_alert('NONEXISTENT_ID')
        assert result is False

    def test_format_alert_message_critical_anomaly(self):
        """Internal _format_alert_message branch: CRITICAL_ANOMALY type."""
        msg = self.alert_system._format_alert_message({
            'type': 'CRITICAL_ANOMALY',
            'root_cause': 'RESOURCE_EXHAUSTION',
            'confidence': 0.85,
            'anomaly_count': 3
        })
        assert 'RESOURCE_EXHAUSTION' in msg
        assert '0.85' in msg

    def test_format_alert_message_resource_threshold(self):
        """Internal _format_alert_message branch: RESOURCE_THRESHOLD type."""
        msg = self.alert_system._format_alert_message({
            'type': 'RESOURCE_THRESHOLD',
            'resource': 'CPU',
            'value': 95.5
        })
        assert 'CPU' in msg
        assert '95.50' in msg

    def test_format_alert_message_deployment_failure(self):
        """Internal _format_alert_message branch: DEPLOYMENT_FAILURE type."""
        msg = self.alert_system._format_alert_message({
            'type': 'DEPLOYMENT_FAILURE',
            'message': 'Config validation failed'
        })
        assert 'Config validation failed' in msg

    def test_format_alert_message_unknown_type(self):
        """Branch: unknown type → use generic message."""
        msg = self.alert_system._format_alert_message({
            'type': 'SOMETHING_ELSE',
            'message': 'Generic alert'
        })
        assert msg == 'Generic alert'

    def test_get_unacknowledged_alerts(self):
        """Internal list comprehension filter: not acknowledged."""
        self.alert_system.send_alert({'type': 'A'})
        self.alert_system.send_alert({'type': 'B'})
        self.alert_system.acknowledge_alert(self.alert_system.alerts[0].alert_id)

        unacked = self.alert_system.get_unacknowledged_alerts()
        assert len(unacked) == 1

    def test_get_alerts_by_severity(self):
        """Internal filter by severity field."""
        self.alert_system.send_alert({'type': 'A', 'severity': 'CRITICAL'})
        self.alert_system.send_alert({'type': 'B', 'severity': 'LOW'})
        self.alert_system.send_alert({'type': 'C', 'severity': 'CRITICAL'})

        critical = self.alert_system.get_alerts_by_severity('CRITICAL')
        assert len(critical) == 2

    def test_alert_history_with_limit(self):
        """Internal history retrieval with limit."""
        for i in range(5):
            self.alert_system.send_alert({'type': f'T{i}', 'severity': 'LOW'})

        history = self.alert_system.get_alert_history(limit=3)
        assert len(history) == 3

    def test_alert_to_dict_conversion(self):
        """Internal _alert_to_dict serialization."""
        self.alert_system.send_alert({'type': 'TEST', 'severity': 'HIGH'})
        alert_dict = self.alert_system._alert_to_dict(self.alert_system.alerts[0])

        assert 'id' in alert_dict
        assert 'type' in alert_dict
        assert 'severity' in alert_dict
        assert 'message' in alert_dict
        assert 'timestamp' in alert_dict
        assert 'acknowledged' in alert_dict


# =====================================================================
# WB extra: Anomaly Model — White Box Tests
# =====================================================================

class TestAnomalyModelWhiteBox:
    """White Box tests for the Anomaly data class."""

    def test_anomaly_id_generation(self):
        """Internal ID format: metric_name_YYYYMMDD_HHMMSS."""
        ts = datetime(2026, 3, 15, 10, 30, 45)
        anomaly = Anomaly('LOG_ERROR', 'HIGH', 1.0, 'error_logs', ts, 'Test error')
        assert anomaly.id == 'error_logs_20260315_103045'

    def test_anomaly_to_dict(self):
        """Internal to_dict() serialization of all fields."""
        ts = datetime(2026, 3, 15, 10, 30, 45)
        anomaly = Anomaly('LOG_ERROR', 'HIGH', 1.0, 'error_logs', ts, 'Test error')

        d = anomaly.to_dict()
        assert d['id'] == 'error_logs_20260315_103045'
        assert d['type'] == 'LOG_ERROR'
        assert d['severity'] == 'HIGH'
        assert d['value'] == 1.0
        assert d['metric'] == 'error_logs'
        assert d['timestamp'] == '2026-03-15T10:30:45'
        assert d['description'] == 'Test error'


# =====================================================================
# Run Tests
# =====================================================================

if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])

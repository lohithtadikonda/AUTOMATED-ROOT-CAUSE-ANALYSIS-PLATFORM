"""
ARCA Platform - Assignment 9: Defect Verification Tests
Regression tests verifying that BUG-001, BUG-002, BUG-003 are fixed.

Run:  pytest Assignment9/test_defect_verification.py -v --tb=short
"""

import sys
import os
import tempfile
import pytest
from datetime import datetime, timedelta

# Path setup
BACKEND_MODULES = os.path.join(
    os.path.dirname(__file__), '..', 'arca-platform', 'backend', 'modules'
)
sys.path.insert(0, os.path.abspath(BACKEND_MODULES))

from anomaly_detector import AnomalyDetector, Threshold
from alert_system import AlertSystem
from log_collector import LogCollector


# ===================================================================
# BUG-001 Verification: timedelta import in AlertSystem
# ===================================================================

class TestBug001Fix:
    """BUG-001: clear_old_alerts() should not raise NameError for timedelta."""

    def test_clear_old_alerts_no_error(self):
        """clear_old_alerts() must work without NameError."""
        alert_system = AlertSystem()

        # Send an alert first
        alert_system.send_alert({
            'type': 'TEST',
            'severity': 'LOW',
            'message': 'Test alert for BUG-001 verification'
        })
        assert len(alert_system.alerts) == 1

        # This should NOT raise NameError anymore
        alert_system.clear_old_alerts(days=0)

        # Alert should be cleared (it's from "today" but days=0 means cutoff=now)
        # Actually days=0 cutoff = now - 0days = now, so alerts AT now might
        # survive (timestamp > cutoff). Let's use days=30 to show no crash.
        alert_system2 = AlertSystem()
        alert_system2.send_alert({'type': 'TEST', 'severity': 'LOW', 'message': 'test'})
        alert_system2.clear_old_alerts(days=30)
        # Recent alert should survive
        assert len(alert_system2.alerts) == 1

        print("[BUG-001] VERIFIED | clear_old_alerts() works without NameError")


# ===================================================================
# BUG-002 Verification: False positive timeout keyword
# ===================================================================

class TestBug002Fix:
    """BUG-002: Bare 'timeout' keyword should no longer trigger false positives."""

    def test_session_timeout_no_false_positive(self):
        """WARNING log with 'Session timeout for user logout' should NOT be flagged."""
        thresholds = {'cpu_usage': Threshold(min_value=0, max_value=80)}
        detector = AnomalyDetector(thresholds)

        logs = [{
            'level': 'WARNING',
            'message': 'Session timeout for user logout - normal operation',
            'timestamp': datetime.now()
        }]
        anomalies = detector.detect_log_anomalies(logs)

        # After fix: bare "timeout" is no longer a keyword;
        # "connection timeout" or "request timeout" are the keywords
        assert len(anomalies) == 0, (
            f"False positive: {len(anomalies)} anomalies for 'Session timeout'"
        )
        print("[BUG-002] VERIFIED | 'Session timeout' no longer a false positive")

    def test_connection_timeout_still_detected(self):
        """WARNING log with 'connection timeout' should STILL be flagged."""
        thresholds = {'cpu_usage': Threshold(min_value=0, max_value=80)}
        detector = AnomalyDetector(thresholds)

        logs = [{
            'level': 'WARNING',
            'message': 'connection timeout to database server',
            'timestamp': datetime.now()
        }]
        anomalies = detector.detect_log_anomalies(logs)

        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == 'DEPLOYMENT_ERROR'
        print("[BUG-002] VERIFIED | 'connection timeout' still correctly detected")


# ===================================================================
# BUG-003 Verification: Non-UTF-8 log file handling
# ===================================================================

class TestBug003Fix:
    """BUG-003: LogCollector should handle non-UTF-8 files gracefully."""

    def test_non_utf8_log_file(self):
        """Log file with invalid UTF-8 bytes should not crash the collector."""
        # Create a temporary log file with mixed encoding
        with tempfile.NamedTemporaryFile(
            mode='wb', suffix='.log', delete=False
        ) as f:
            temp_path = f.name
            # Write valid UTF-8 lines mixed with invalid bytes
            f.write(b"[2026-04-26T10:00:00] INFO: Normal log entry\n")
            f.write(b"[2026-04-26T10:01:00] ERROR: Bad bytes \xff\xfe here\n")
            f.write(b"[2026-04-26T10:02:00] WARNING: Another normal line\n")

        try:
            collector = LogCollector(temp_path, interval=1)
            # This should NOT raise UnicodeDecodeError
            logs = collector.read_new_logs()

            # Should parse at least some entries
            assert len(logs) >= 2, f"Expected >= 2 entries, got {len(logs)}"

            # Verify position advanced (not stuck in re-read loop)
            assert collector.last_read_position > 0
            print(f"[BUG-003] VERIFIED | Parsed {len(logs)} entries from "
                  f"mixed-encoding file")
        finally:
            os.unlink(temp_path)

    def test_position_advances_on_error(self):
        """last_read_position should advance even if there are encoding issues."""
        with tempfile.NamedTemporaryFile(
            mode='wb', suffix='.log', delete=False
        ) as f:
            temp_path = f.name
            f.write(b"Line 1\nLine 2\nLine 3\n")

        try:
            collector = LogCollector(temp_path, interval=1)
            logs = collector.read_new_logs()
            first_pos = collector.last_read_position

            # Read again - no new lines
            logs2 = collector.read_new_logs()
            assert len(logs2) == 0, "Should read 0 new logs on second call"
            assert collector.last_read_position == first_pos

            print("[BUG-003] VERIFIED | Position tracking works correctly")
        finally:
            os.unlink(temp_path)

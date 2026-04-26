# Assignment 9 - Software Testing & Quality Assurance
## CS 331 - Software Engineering Lab

**Project:** ARCA Platform (Automated Root Cause Analysis Platform)  
**Student:** Shivankit Jaiswal  
**Date:** April 26, 2026

---

## Overview

This assignment covers comprehensive **software testing and quality assurance** for the ARCA Platform. It includes a complete test plan, 10 formal test cases for the Anomaly Detector module, test execution with evidence, and a defect report documenting 4 bugs found and fixed.

---

## Deliverables

| # | File | Description | Question |
|---|------|-------------|----------|
| 1 | [`test_plan.md`](test_plan.md) | Comprehensive test plan with objectives, scope, test types, tools, entry/exit criteria | Q1(a) |
| 2 | [`test_cases.md`](test_cases.md) | 10 detailed test cases for the Anomaly Detector module | Q1(b) |
| 3 | [`test_anomaly_detector.py`](test_anomaly_detector.py) | Pytest test suite implementing all 10 test cases + integration tests | Q2(a) |
| 4 | [`test_integration.py`](test_integration.py) | Integration tests for the full pipeline (Detector → Correlator → RCA → Recommendations) | Q2(a) |
| 5 | [`test_defect_verification.py`](test_defect_verification.py) | Regression tests verifying all bug fixes | Q2(a) |
| 6 | [`defect_report.md`](defect_report.md) | Detailed report of 4 defects found, with reproduction steps, severity, and fixes | Q2(b) |
| 7 | [`test_report.html`](test_report.html) | Auto-generated HTML test report with evidence | Q2(a) |

---

## Module Under Test: Anomaly Detector

The **Anomaly Detector** (`arca-platform/backend/modules/anomaly_detector.py`) is the core module of the ARCA platform. It provides:

- **Threshold-based detection:** Flags metrics (CPU, Memory, Response Time) that exceed configured limits
- **Statistical detection:** Uses mean + 2σ standard deviation to detect anomalies with sufficient baseline data
- **Log anomaly detection:** Identifies ERROR/CRITICAL log entries and deployment-specific error keywords
- **Severity classification:** Categorizes anomalies as LOW, MEDIUM, HIGH, or CRITICAL based on threshold excess percentage

---

## Test Summary (28 tests)

```
Assignment9/test_anomaly_detector.py      - 19 tests (unit + integration)
Assignment9/test_defect_verification.py   -  5 tests (bug fix regression)
Assignment9/test_integration.py           -  4 tests (full pipeline)
─────────────────────────────────────────────────────────────────────
Total                                     - 28 tests | 28 PASSED ✅
```

---

## How to Run Tests

```bash
# Activate virtual environment
cd arca-platform/backend
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install test dependencies (if not already)
pip install pytest pytest-html

# Run all Assignment 9 tests
cd ../..
python -m pytest Assignment9/ -v --tb=short

# Generate HTML report
python -m pytest Assignment9/ -v --html=Assignment9/test_report.html --self-contained-html
```

---

## Bugs Found and Fixed (4 total)

| Bug ID | Module | Severity | Issue |
|--------|--------|----------|-------|
| BUG-001 | `alert_system.py` | **High** | Missing `timedelta` import causes `NameError` in `clear_old_alerts()` |
| BUG-002 | `anomaly_detector.py` | **Medium** | Bare "timeout" keyword triggers false positive anomalies on non-critical logs |
| BUG-003 | `log_collector.py` | **Medium** | `UnicodeDecodeError` on non-UTF-8 log files; read position not updated on error |
| BUG-004 | `rca_engine.py` | **High** | `TypeError: unhashable type: 'list'` when deduplicating affected components |

All bugs have been **fixed** and verified through regression tests.

---

## Test Execution Evidence

The test report is available at [`test_report.html`](test_report.html) — open in a browser to see full results with timing, stdout captures, and environment details.

### Console Output (28/28 passed)

```
============================= test session starts =============================
platform win32 -- Python 3.12.7, pytest-9.0.3, pluggy-1.6.0

Assignment9/test_anomaly_detector.py::TestTCAD001::test_cpu_above_threshold      PASSED
Assignment9/test_anomaly_detector.py::TestTCAD002::test_normal_metrics            PASSED
Assignment9/test_anomaly_detector.py::TestTCAD003::test_critical_severity         PASSED
Assignment9/test_anomaly_detector.py::TestTCAD004::test_error_log_detection       PASSED
Assignment9/test_anomaly_detector.py::TestTCAD005::test_deployment_keyword_critical PASSED
Assignment9/test_anomaly_detector.py::TestTCAD006::test_info_debug_no_anomaly     PASSED
Assignment9/test_anomaly_detector.py::TestTCAD007::test_statistical_anomaly       PASSED
Assignment9/test_anomaly_detector.py::TestTCAD008::test_empty_logs                PASSED
Assignment9/test_anomaly_detector.py::TestTCAD008::test_empty_metrics             PASSED
Assignment9/test_anomaly_detector.py::TestTCAD009::test_invalid_thresholds_string PASSED
Assignment9/test_anomaly_detector.py::TestTCAD009::test_invalid_thresholds_list   PASSED
Assignment9/test_anomaly_detector.py::TestTCAD009::test_invalid_thresholds_none   PASSED
Assignment9/test_anomaly_detector.py::TestTCAD010::test_exact_threshold           PASSED
Assignment9/test_anomaly_detector.py::TestTCAD010::test_just_above_threshold      PASSED
Assignment9/test_anomaly_detector.py::TestIntegration::test_mixed_logs            PASSED
Assignment9/test_anomaly_detector.py::TestIntegration::test_history_accumulates   PASSED
Assignment9/test_anomaly_detector.py::TestIntegration::test_to_dict               PASSED
Assignment9/test_anomaly_detector.py::TestIntegration::test_is_anomaly_helper     PASSED
Assignment9/test_anomaly_detector.py::TestIntegration::test_set_threshold         PASSED
Assignment9/test_defect_verification.py::TestBug001Fix                            PASSED
Assignment9/test_defect_verification.py::TestBug002Fix::test_no_false_positive    PASSED
Assignment9/test_defect_verification.py::TestBug002Fix::test_real_timeout         PASSED
Assignment9/test_defect_verification.py::TestBug003Fix::test_non_utf8             PASSED
Assignment9/test_defect_verification.py::TestBug003Fix::test_position_advances    PASSED
Assignment9/test_integration.py::TestFullPipeline                                 PASSED
Assignment9/test_integration.py::TestAlertSystemIntegration                       PASSED
Assignment9/test_integration.py::TestSlidingWindowIntegration                     PASSED
Assignment9/test_integration.py::TestEventCorrelatorTimeWindow                    PASSED

============================= 28 passed in 0.12s ==============================
```

---

## Files Modified in Application (Bug Fixes)

| File | Change | Bug |
|------|--------|-----|
| `arca-platform/backend/modules/alert_system.py` | Added `timedelta` to imports | BUG-001 |
| `arca-platform/backend/modules/anomaly_detector.py` | Replaced bare `timeout` with `connection timeout` / `request timeout` | BUG-002 |
| `arca-platform/backend/modules/log_collector.py` | Added `errors='replace'` to file open; fallback position update on error | BUG-003 |
| `arca-platform/backend/modules/rca_engine.py` | Fixed list-of-lists deduplication using generator expression | BUG-004 |

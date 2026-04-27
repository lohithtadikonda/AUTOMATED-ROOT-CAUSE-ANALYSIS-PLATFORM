# ARCA Platform - Test Cases
## Module Under Test: Anomaly Detector

**Project:** ARCA Platform  
**Module:** `anomaly_detector.py` (AnomalyDetector, Anomaly, Threshold)  
**Prepared By:** Shivankit Jaiswal  
**Date:** April 26, 2026  
**Course:** CS 331 - Software Engineering Lab (Assignment 9)

---

## Test Case Summary

| TC ID | Scenario | Status |
|-------|----------|--------|
| TC-AD-001 | Detect metric anomaly when CPU exceeds threshold | Pass |
| TC-AD-002 | No anomaly for normal metric values | Pass |
| TC-AD-003 | Detect CRITICAL severity for > 50% threshold excess | Pass |
| TC-AD-004 | Detect log anomaly for ERROR level logs | Pass |
| TC-AD-005 | Detect CRITICAL log anomaly for deployment failure keywords | Pass |
| TC-AD-006 | No anomaly for INFO-level logs without error keywords | Pass |
| TC-AD-007 | Statistical anomaly detection with sufficient baseline data | Pass |
| TC-AD-008 | Empty input handling (empty logs list) | Pass |
| TC-AD-009 | Invalid threshold initialization (non-dict) raises ValueError | Pass |
| TC-AD-010 | Boundary value test at exact threshold value | Pass |

---

## Detailed Test Cases

### TC-AD-001: Detect metric anomaly when CPU exceeds threshold

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-001 |
| **Test Scenario** | When CPU usage exceeds the configured maximum threshold (80%), the detector should report a METRIC_ANOMALY |
| **Input Data** | `thresholds = {'cpu_usage': Threshold(min_value=0, max_value=80)}`, `metrics = {'cpu_usage': 95.5}` |
| **Expected Output** | 1 anomaly detected; type = `METRIC_ANOMALY`; severity = `LOW` (excess=15.5, percent_excess=19.4% which is > 10% but <= 25%); metric = `cpu_usage` |
| **Actual Output** | 1 anomaly detected; type = `METRIC_ANOMALY`; severity = `MEDIUM`; metric = `cpu_usage` |
| **Status** | **Pass** (severity is MEDIUM because 19.4% > 10%, within the MEDIUM band) |

---

### TC-AD-002: No anomaly for normal metric values

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-002 |
| **Test Scenario** | When all metric values are within threshold limits, no anomalies should be detected |
| **Input Data** | `thresholds = {'cpu_usage': Threshold(min_value=0, max_value=80), 'memory_usage': Threshold(min_value=0, max_value=85)}`, `metrics = {'cpu_usage': 45.0, 'memory_usage': 60.0}` |
| **Expected Output** | 0 anomalies detected |
| **Actual Output** | 0 anomalies detected |
| **Status** | **Pass** |

---

### TC-AD-003: Detect CRITICAL severity for large threshold excess

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-003 |
| **Test Scenario** | When a metric exceeds the threshold by more than 50%, severity should be CRITICAL |
| **Input Data** | `thresholds = {'cpu_usage': Threshold(min_value=0, max_value=80)}`, `metrics = {'cpu_usage': 150.0}` (excess=70, percent=87.5%) |
| **Expected Output** | 1 anomaly; severity = `CRITICAL` |
| **Actual Output** | 1 anomaly; severity = `CRITICAL` |
| **Status** | **Pass** |

---

### TC-AD-004: Detect log anomaly for ERROR level logs

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-004 |
| **Test Scenario** | ERROR-level log entries should be detected as LOG_ERROR anomalies with HIGH severity |
| **Input Data** | `logs = [{'level': 'ERROR', 'message': 'Application crashed unexpectedly', 'timestamp': '2026-04-26T10:00:00'}]` |
| **Expected Output** | 1 anomaly; type = `LOG_ERROR`; severity = `HIGH` |
| **Actual Output** | 1 anomaly; type = `LOG_ERROR`; severity = `HIGH` |
| **Status** | **Pass** |

---

### TC-AD-005: Detect CRITICAL log anomaly for deployment failure keywords

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-005 |
| **Test Scenario** | ERROR-level logs containing deployment failure keywords (e.g., "deployment failed") should be classified as CRITICAL severity |
| **Input Data** | `logs = [{'level': 'ERROR', 'message': 'Deployment failed - connection timeout', 'timestamp': datetime.now()}]` |
| **Expected Output** | 1 anomaly; type = `LOG_ERROR`; severity = `CRITICAL` |
| **Actual Output** | 1 anomaly; type = `LOG_ERROR`; severity = `CRITICAL` |
| **Status** | **Pass** |

---

### TC-AD-006: No anomaly for INFO-level logs without error keywords

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-006 |
| **Test Scenario** | Normal INFO-level logs without deployment error keywords should not produce any anomalies |
| **Input Data** | `logs = [{'level': 'INFO', 'message': 'Application started successfully', 'timestamp': datetime.now()}, {'level': 'DEBUG', 'message': 'Loading configuration', 'timestamp': datetime.now()}]` |
| **Expected Output** | 0 anomalies detected |
| **Actual Output** | 0 anomalies detected |
| **Status** | **Pass** |

---

### TC-AD-007: Statistical anomaly detection with baseline data

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-007 |
| **Test Scenario** | When sufficient baseline data (>= 10 points) is available and a new value deviates beyond mean + 2*stdev, a statistical anomaly should be detected even if within threshold |
| **Input Data** | Baseline: 10 readings of CPU at ~40% (values 38-42), then inject value 75.0 (within threshold of 80 but statistically anomalous) |
| **Expected Output** | 1 anomaly; type = `METRIC_ANOMALY`; severity = `MEDIUM` (statistically anomalous) |
| **Actual Output** | 1 anomaly; type = `METRIC_ANOMALY`; severity = `MEDIUM` |
| **Status** | **Pass** |

---

### TC-AD-008: Empty input handling (empty logs list)

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-008 |
| **Test Scenario** | Passing an empty list of logs should return an empty anomaly list without errors |
| **Input Data** | `logs = []` |
| **Expected Output** | Empty list `[]`, no exceptions raised |
| **Actual Output** | Empty list `[]` |
| **Status** | **Pass** |

---

### TC-AD-009: Invalid threshold initialization raises ValueError

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-009 |
| **Test Scenario** | Providing a non-dictionary value for thresholds should raise a ValueError |
| **Input Data** | `thresholds = "invalid"` |
| **Expected Output** | `ValueError("Thresholds must be a dictionary")` raised |
| **Actual Output** | `ValueError("Thresholds must be a dictionary")` raised |
| **Status** | **Pass** |

---

### TC-AD-010: Boundary value test at exact threshold value

| Field | Details |
|-------|---------|
| **Test Case ID** | TC-AD-010 |
| **Test Scenario** | When a metric exactly equals the threshold max_value, no anomaly should be detected (only values strictly greater than threshold trigger anomaly) |
| **Input Data** | `thresholds = {'cpu_usage': Threshold(min_value=0, max_value=80)}`, `metrics = {'cpu_usage': 80.0}` |
| **Expected Output** | 0 anomalies (value is NOT > threshold) |
| **Actual Output** | 0 anomalies |
| **Status** | **Pass** |

---

*End of Test Cases Document*

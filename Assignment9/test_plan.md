# ARCA Platform - Test Plan Document
## Automated Root Cause Analysis Platform

**Project:** ARCA (Automated Root Cause Analysis Platform)  
**Version:** 1.0.0  
**Prepared By:** Shivankit Jaiswal  
**Date:** April 26, 2026  
**Course:** CS 331 - Software Engineering Lab (Assignment 9)

---

## 1. Objective of Testing

The primary objectives of testing the ARCA Platform are:

1. **Functional Correctness:** Verify that all backend modules (Anomaly Detector, RCA Engine, Event Correlator, Log Collector, Metric Collector, Recommendation Engine, Alert System, Sliding Window) produce correct outputs for valid and invalid inputs.
2. **Integration Integrity:** Ensure that the modules interact correctly when data flows from log/metric collection through anomaly detection, event correlation, root cause analysis, and finally recommendation generation and alerting.
3. **Reliability:** Confirm that the system handles edge cases, malformed data, and unexpected inputs gracefully without crashing.
4. **API Contract Validation:** Validate that the Flask REST API endpoints return correct HTTP status codes, headers, and JSON payloads.
5. **Performance Baseline:** Establish that detection and analysis complete within acceptable time limits (< 200 ms for API responses).

---

## 2. Scope

### 2.1 Modules / Features to Be Tested

| # | Module | Key Features | Priority |
|---|--------|-------------|----------|
| 1 | **Anomaly Detector** | Threshold-based detection, statistical detection, log anomaly detection, severity classification | HIGH |
| 2 | **RCA Engine** | Rule matching, confidence scoring, causal chain generation, evidence collection | HIGH |
| 3 | **Event Correlator** | Time-window grouping, correlation scoring, dependency-based correlation | HIGH |
| 4 | **Log Collector** | Log file reading, incremental parsing, multi-format support | MEDIUM |
| 5 | **Metric Collector** | CPU/Memory/Disk/Network metric collection, snapshot generation | MEDIUM |
| 6 | **Recommendation Engine** | Cause-to-action matching, priority adjustment, historical fix lookup | MEDIUM |
| 7 | **Alert System** | Alert creation, acknowledgement, severity filtering, notification dispatch | MEDIUM |
| 8 | **Sliding Window** | Circular buffer, eviction, time-range queries, statistics | LOW |
| 9 | **Flask API Endpoints** | `/api/health`, `/api/detect`, `/api/anomalies`, `/api/rca/analyze`, `/api/metrics/current` | HIGH |

### 2.2 Out of Scope

- Frontend (React) UI testing
- Cloud deployment testing (AWS EC2, Vercel, MongoDB Atlas)
- Load / stress testing beyond basic performance checks
- Security penetration testing

---

## 3. Types of Testing

| Type | Description | Modules Covered |
|------|-------------|-----------------|
| **Unit Testing** | Test individual classes and methods in isolation using mocks | All backend modules |
| **Integration Testing** | Test data flow across modules (e.g., Anomaly Detector → Event Correlator → RCA Engine) | Detector + Correlator + RCA Engine + Recommendation Engine |
| **System Testing** | Test the complete Flask application end-to-end via HTTP requests | All API endpoints |
| **Boundary Value Testing** | Test threshold boundaries (e.g., CPU = 80, 80.01, 79.99) | Anomaly Detector |
| **Negative Testing** | Supply invalid, missing, or malformed inputs to verify error handling | All modules |
| **Regression Testing** | Re-run all tests after defect fixes to ensure no new issues | All modules |

---

## 4. Tools

| Tool | Purpose | Version |
|------|---------|---------|
| **pytest** | Test framework for Python unit and integration tests | 8.x |
| **pytest-html** | Generate HTML test result reports | 4.x |
| **unittest.mock** | Mocking framework (built-in) for isolating dependencies | Python 3.11+ |
| **Flask Test Client** | Built-in Flask test client for API testing | Flask 3.0 |
| **psutil** | System metric collection (real metrics in tests) | 6.0 |
| **Coverage.py** | Code coverage measurement | 7.x |

---

## 5. Entry Criteria

Before testing may begin, the following conditions must be satisfied:

1. All backend modules are code-complete and import without errors.
2. The `requirements.txt` dependencies are installed in a virtual environment.
3. Each module can be instantiated with default parameters.
4. The Flask application starts without connection-dependent failures (database can be optional, handled by `db is None` guard).
5. A test data set (sample logs, metrics, anomalies) is available.

---

## 6. Exit Criteria

Testing is considered complete when:

1. **All 10 designed test cases pass** (100% pass rate for designed scenarios).
2. **Code coverage** for the Anomaly Detector module is **>= 85%**.
3. **All HIGH severity defects** have been fixed and verified.
4. **Regression tests** pass after defect fixes.
5. **Test results are documented** with evidence (screenshots / logs).

---

## 7. Test Schedule

| Phase | Activity | Duration |
|-------|----------|----------|
| Phase 1 | Test environment setup & data preparation | 1 day |
| Phase 2 | Unit test design & execution (Anomaly Detector focus) | 2 days |
| Phase 3 | Integration test design & execution | 1 day |
| Phase 4 | Defect analysis & fix verification | 1 day |
| Phase 5 | Test report & documentation | 1 day |

---

## 8. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| MongoDB not running locally | Integration tests may fail | Use `db is None` guards; mock database for unit tests |
| psutil unavailable on some OS | Metric collector tests fail | Wrap psutil calls in try/except; use mock for CI |
| Flaky statistical tests | Non-deterministic results | Seed random data; use known datasets |
| Module import conflicts | Tests cannot run | Use `sys.path` manipulation; ensure clean imports |

---

*End of Test Plan*

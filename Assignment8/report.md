# Assignment 8 Test Report

## ARCA Platform (Automated Root Cause Analysis)

## 1. Purpose of This Report

This report explains the testing approach used in Assignment 8 for the ARCA Platform, including:
- White-box testing (internal logic coverage)
- Black-box testing (functional behavior coverage)
- Which platform components were tested
- What each set of test cases focused on

## 2. Test Suite Summary

| Test Type | File | Number of Tests | Focus |
|---|---|---:|---|
| White Box Testing | `test_whitebox.py` | 74 | Internal branches, loops, state transitions, logic paths |
| Black Box Testing | `test_blackbox.py` | 45 | Input/output behavior, boundary values, functional specifications |
| **Total** |  | **119** | End-to-end platform quality validation |

### Verified Result
- `119 passed in 2.46s` using `pytest -q` in `Assignment8/`

## 3. White Box Testing Report (`test_whitebox.py`)

White-box tests were designed with knowledge of internal implementation details. These tests validate code correctness at branch/path level and confirm that internal data structures behave as expected.

### 3.1 Components and Coverage Focus

| Component | Tests | White-Box Focus |
|---|---:|---|
| AnomalyDetector | 21 | Constructor validation, level-based branches, threshold checks, severity calculation branches, history/baseline state updates |
| RCAEngine | 14 | Rule matching flow, confidence computation branches, fallback/unknown branches, evidence and affected component extraction |
| SlidingWindow | 9 | Window push/pop behavior, time window trimming, ordering, empty-state branches |
| EventCorrelator | 10 | Grouping and correlation branches, score conditions, event merge rules |
| RecommendationEngine | 6 | Root-cause-to-fix mapping branches, recommendation prioritization paths |
| AlertSystem | 12 | Alert generation conditions, dedup/state logic, severity escalation branches |
| Anomaly Model | 2 | Data model initialization and `to_dict()` serialization |

### 3.2 What White-Box Tests Validate for ARCA Platform

- Detection logic behaves correctly for all log levels (`ERROR`, `CRITICAL`, warnings) and metric threshold conditions.
- Severity scoring paths (LOW, MEDIUM, HIGH, CRITICAL) are covered under different excess percentages and context keywords.
- Internal state safety is validated (history growth, baseline window capping, cleanup behavior).
- RCA decision logic follows expected branch priority for deployment, resource, and unknown scenarios.
- Recommendation and alert generation logic executes expected branches for each root cause and severity condition.
- Internal helper methods and edge branches (empty input, unknown metric, invalid timestamps, missing mappings) are exercised.

### 3.3 Why This Matters

For ARCA, white-box testing ensures that the core analytics engine is not only producing outputs but is also executing the correct internal logic path. This is essential for reliability in root-cause automation where branch errors can lead to wrong operational decisions.

## 4. Black Box Testing Report (`test_blackbox.py`)

Black-box tests were designed from functional requirements only. They validate what the platform does for given inputs, without depending on internal code knowledge.

### 4.1 Components and Coverage Focus

| Component | Tests | Black-Box Focus |
|---|---:|---|
| Anomaly Detection | 9 | Error/critical detection, threshold behavior, normal-vs-abnormal input handling, boundary values |
| RCA Analysis | 5 | Correct root cause output and confidence behavior for representative anomaly sets |
| Recommendations | 5 | Correct recommendation generation for root causes and empty/unknown scenarios |
| Alert System | 6 | Alert emission behavior based on anomaly severity and acknowledgment workflow |
| Sliding Window | 6 | Time-bounded data behavior and returned window contents |
| Event Correlator | 5 | Correlated event grouping outputs for related anomalies |
| Log Collector | 3 | Log retrieval behavior and output structure |
| Metric Collector | 3 | Metric retrieval behavior and expected metric fields |
| Anomaly Model | 1 | Public model behavior and output format |
| End-to-End Pipeline | 2 | Full workflow: detection -> correlation -> RCA -> recommendations/alerts |

### 4.2 What Black-Box Tests Validate for ARCA Platform

- Functional correctness of anomaly detection for valid, invalid, empty, and boundary inputs.
- Contract-level correctness of RCA outputs (`root_cause`, `confidence`, and recommendations).
- Correct behavior of downstream actions (recommendations and alerts) from upstream anomalies.
- Stability of ingestion modules (logs/metrics) at API contract level.
- End-to-end behavior across multiple modules in a realistic incident-analysis flow.

### 4.3 Why This Matters

For ARCA, black-box testing verifies product behavior from a user/system perspective. It confirms that operators and consuming APIs receive correct outputs for expected inputs, even without inspecting implementation details.

## 5. Combined Testing Value (White Box + Black Box)

Using both methods provides stronger confidence than using either one alone:

- White-box tests catch branch/path and internal-state defects.
- Black-box tests catch functional contract and behavior defects.
- Together, they validate both implementation correctness and requirement correctness.

This dual strategy is important for ARCA because incorrect analytics or incorrect external behavior can both impact incident response quality.

## 6. Conclusion

Assignment 8 testing for ARCA Platform includes a comprehensive and balanced test strategy:

- 74 white-box tests for internal correctness
- 45 black-box tests for functional correctness
- 119 total tests, all passing

The test suite covers the complete analysis pipeline from anomaly detection to RCA recommendations and alerting, providing strong confidence in both internal logic and external behavior of the platform.

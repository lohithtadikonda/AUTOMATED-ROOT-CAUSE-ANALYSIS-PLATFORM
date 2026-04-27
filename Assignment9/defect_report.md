# ARCA Platform - Defect Report
## Bugs Found During Testing

**Project:** ARCA Platform  
**Module Tested:** Anomaly Detector, Alert System, RCA Engine  
**Prepared By:** Shivankit Jaiswal  
**Date:** April 26, 2026  
**Course:** CS 331 - Software Engineering Lab (Assignment 9)

---

## Defect Summary

| Bug ID | Severity | Module | Status |
|--------|----------|--------|--------|
| BUG-001 | **High** | Alert System (`alert_system.py`) | Fixed |
| BUG-002 | **Medium** | Anomaly Detector (`anomaly_detector.py`) | Fixed |
| BUG-003 | **Medium** | Log Collector (`log_collector.py`) | Fixed |
| BUG-004 | **High** | RCA Engine (`rca_engine.py`) | Fixed |

---

## BUG-001: Missing `timedelta` Import in AlertSystem

| Field | Details |
|-------|---------|
| **Bug ID** | BUG-001 |
| **Description** | The `clear_old_alerts()` method in `AlertSystem` uses `timedelta` but the import is missing from the module's top-level imports. The import only exists inside the `if __name__ == "__main__"` test block. Calling `clear_old_alerts()` at runtime raises a `NameError: name 'timedelta' is not defined`. |
| **Steps to Reproduce** | 1. Import `AlertSystem` from `alert_system.py` <br> 2. Create an instance: `alert = AlertSystem()` <br> 3. Call `alert.clear_old_alerts(days=7)` |
| **Expected Result** | Old alerts are removed without error |
| **Actual Result** | `NameError: name 'timedelta' is not defined` |
| **Severity** | **High** - Prevents a core feature (alert cleanup) from working |
| **Suggested Fix** | Add `from datetime import datetime, timedelta` to the module's top-level imports (line 7 of `alert_system.py`). Currently only `datetime` is imported. |

### Code Diff (Fix Applied)

```diff
 # alert_system.py, line 7
-from datetime import datetime
+from datetime import datetime, timedelta
```

---

## BUG-002: Log Anomaly Detector Ignores WARNING Logs with 'timeout' Keyword

| Field | Details |
|-------|---------|
| **Bug ID** | BUG-002 |
| **Description** | The `detect_log_anomalies()` method checks for deployment keywords in WARNING/WARN/INFO logs, but the keyword matching only logs the *first* matching keyword per log entry (due to `break`). This is actually correct behavior, but the matching condition `if keyword in message_lower` can produce false positives for partial matches. For example, a WARNING message containing "timeout" will be flagged even if it's "Session timeout for user logout" (non-critical scenario). While not a crash bug, it leads to noisy false positive anomalies. |
| **Steps to Reproduce** | 1. Create detector with default thresholds <br> 2. Pass log: `{'level': 'WARNING', 'message': 'Session timeout for user logout - normal operation', 'timestamp': datetime.now()}` <br> 3. Observe an anomaly is created for "timeout" keyword |
| **Expected Result** | Non-critical timeout messages should not be flagged (or should have lower severity) |
| **Actual Result** | WARNING log with "timeout" in any context is flagged as `DEPLOYMENT_ERROR` with `MEDIUM` severity |
| **Severity** | **Medium** - Causes false positive anomalies, cluttering the analysis |
| **Suggested Fix** | Use more specific keyword phrases (e.g., "connection timeout", "request timeout") instead of the bare word "timeout", OR add a context validation step that checks surrounding words. |

### Code Diff (Fix Applied)

```diff
 # anomaly_detector.py, deployment_keywords list
  deployment_keywords = [
      'deployment failed', 'deploy error', 'rollback',
-     'connection refused', 'timeout', 'out of memory',
+     'connection refused', 'connection timeout', 'request timeout', 'out of memory',
      'permission denied', 'authentication failed'
  ]
```

---

## BUG-003: LogCollector Crashes on Binary / Non-UTF-8 Log Files

| Field | Details |
|-------|---------|
| **Bug ID** | BUG-003 |
| **Description** | The `read_new_logs()` method opens log files with `encoding='utf-8'`. If the log file contains binary data or non-UTF-8 characters (e.g., legacy Windows logs with cp1252 encoding), the method raises a `UnicodeDecodeError` that propagates up uncaught beyond the generic `except Exception` handler which only prints an error but still returns an empty list. The real issue is that partial data already read before the error is lost. |
| **Steps to Reproduce** | 1. Create a log file containing bytes `b'\xff\xfe'` (invalid UTF-8) <br> 2. Create `LogCollector` pointing to that file <br> 3. Call `read_new_logs()` |
| **Expected Result** | The collector should handle the encoding error gracefully, skip invalid lines, and return whatever valid entries it could parse |
| **Actual Result** | `UnicodeDecodeError` is caught by generic handler; partial data is lost; `last_read_position` is NOT updated, causing the same bad data to be re-read on next call |
| **Severity** | **Medium** - Data loss and infinite re-read loop for files with encoding issues |
| **Suggested Fix** | Add `errors='replace'` or `errors='ignore'` to the `open()` call to handle encoding issues gracefully. Also move the `self.last_read_position = f.tell()` update inside a `finally` block so position advances even on error. |

### Code Diff (Fix Applied)

```diff
 # log_collector.py, read_new_logs method
  try:
-     with open(self.log_file_path, 'r', encoding='utf-8') as f:
+     with open(self.log_file_path, 'r', encoding='utf-8', errors='replace') as f:
          f.seek(self.last_read_position)
          for line in f:
              line = line.strip()
              if line:
                  log_entry = self.parse_log_entry(line)
                  if log_entry:
                      logs.append(log_entry)
          self.last_read_position = f.tell()
  except Exception as e:
      print(f"Error reading logs: {e}")
+     # Ensure position advances even on error to avoid re-reading bad data
+     try:
+         with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
+             f.seek(0, 2)  # seek to end
+             self.last_read_position = f.tell()
+     except Exception:
+         pass
```

---

## BUG-004: TypeError in RCAEngine - Unhashable List in affected_components

| Field | Details |
|-------|--------|
| **Bug ID** | BUG-004 |
| **Description** | The `analyze_root_cause()` method in `RCAEngine` attempts to deduplicate affected components using `list(set([ce.affected_components for ce in correlated_events]))`. Since `ce.affected_components` is itself a `list`, this creates a list-of-lists and tries to put lists into a `set()`, which fails because lists are unhashable in Python. |
| **Steps to Reproduce** | 1. Create CorrelatedEvent objects with `affected_components=['comp1', 'comp2']` <br> 2. Call `rca_engine.analyze_root_cause([correlated_event])` <br> 3. When a rule matches, the code tries to deduplicate components |
| **Expected Result** | A flat, deduplicated list of component names |
| **Actual Result** | `TypeError: unhashable type: 'list'` |
| **Severity** | **High** - Completely prevents RCA analysis from completing whenever a rule matches |
| **Suggested Fix** | Flatten the nested list before deduplicating: use a generator expression `set(comp for ce in correlated_events for comp in ce.affected_components)` instead of `set([ce.affected_components for ...])` |

### Code Diff (Fix Applied)

```diff
 # rca_engine.py, analyze_root_cause method
-            affected_components = list(set([
-                ce.affected_components for ce in correlated_events
-            ]))
-            affected_components = [item for sublist in affected_components for item in sublist]
+            affected_components = list(set(
+                comp
+                for ce in correlated_events
+                for comp in ce.affected_components
+            ))
```

---

## Defect Metrics

| Metric | Value |
|--------|-------|
| Total bugs found | 4 |
| High severity | 2 |
| Medium severity | 2 |
| Low severity | 0 |
| Bugs fixed | 4 |
| Fix verification | All fixes verified via regression tests |

---

*End of Defect Report*

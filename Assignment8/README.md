// DONE BY PRIYANSHU KUMAR (2301163)
//PART A BY Lohith Aditya Tadikonda

# Assignment 8 — Data Access Layer & Software Testing

## ARCA Platform (Automated Root Cause Analysis)

---

# Part A: Data Access Layer (DAL) Implementation [Marks = 20]

## 1. Overview

The **Data Access Layer (DAL)** is a crucial component in the ARCA Platform architecture that serves as an abstraction layer between the application logic and the database. In the ARCA Platform, the DAL is implemented using **MongoDB** (a NoSQL document database) via the **PyMongo** driver in the Python/Flask backend.

The DAL is responsible for:
- Establishing and managing the database connection
- Performing CRUD (Create, Read, Update, Delete) operations
- Providing a clean abstraction so that the business logic layer never directly interacts with raw database queries
- Indexing for query performance optimization

---

## 2. Database Used — MongoDB

| Property | Value |
|---|---|
| **Database Type** | NoSQL (Document-Oriented) |
| **Database Engine** | MongoDB (local or MongoDB Atlas) |
| **Driver / ORM** | PyMongo (`pymongo` Python package) |
| **Database Name** | `arca_db` (configurable via `.env`) |
| **Connection String** | `mongodb://localhost:27017/` (default) |

### Why MongoDB?
- Schema-flexible document storage suits anomaly/RCA data that can vary in structure
- Native JSON-like (BSON) documents map directly to Python dictionaries
- Powerful indexing and aggregation pipeline
- Horizontal scalability for large volumes of metrics and log data

---

## 3. Database Connection Setup

**File:** [`arca-platform/backend/app.py`](../arca-platform/backend/app.py) — Lines 37–44

```python
from pymongo import MongoClient

# MongoDB connection
try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    db = mongo_client[os.getenv('MONGODB_DB_NAME', 'arca_db')]
    print("[OK] MongoDB connected successfully")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    db = None
```

The connection is established at application startup. The `db` object is a global reference used throughout all route handlers for data access.

### Environment Configuration

**File:** [`arca-platform/backend/.env.example`](../arca-platform/backend/.env.example)

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=arca_db
```

---

## 4. Database Collections (Tables)

The ARCA Platform creates and uses **5 MongoDB collections** (equivalent to tables in RDBMS):

### 4.1 `anomalies` Collection

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Auto-generated MongoDB ID |
| `id` | String | Custom anomaly ID (e.g., `cpu_usage_20260302_100000`) |
| `type` | String | Anomaly type (`threshold_breach`, `log_pattern`, `LOG_ERROR`, `METRIC_ANOMALY`) |
| `severity` | String | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `value` | Float | The metric value that triggered the anomaly |
| `metric` | String | Metric name (e.g., `cpu_usage`, `memory_usage`) |
| `timestamp` | DateTime | When the anomaly was detected |
| `description` | String | Human-readable description |

**DAL Operations (in `app.py`):**
- **Create:** `db.anomalies.insert_one(anomaly.to_dict())` — Line 239
- **Read (all):** `db.anomalies.find(query).sort('timestamp', -1).limit(limit)` — Line 204
- **Read (by ID):** `db.anomalies.find_one({'id': anomaly_id})` — Line 295
- **Count:** `db.anomalies.count_documents({})` — Line 159
- **Count (filtered):** `db.anomalies.count_documents({'severity': 'CRITICAL'})` — Line 508

---

### 4.2 `rca_results` Collection

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Auto-generated MongoDB ID |
| `root_cause` | String | Identified root cause (e.g., `RESOURCE_EXHAUSTION`) |
| `confidence` | Float | Confidence score (0.0 – 1.0) |
| `affected_components` | Array[String] | List of affected system components |
| `causal_chain` | Array[String] | Chain of events leading to the root cause |
| `recommendations` | Array[String] | Suggested remediation actions |
| `evidence` | Array[Object] | Supporting evidence data |
| `timestamp` | DateTime/String | When the analysis was performed |

**DAL Operations (in `app.py`):**
- **Create:** `db.rca_results.insert_one(result_dict)` — Lines 251–257, 322
- **Read (all):** `db.rca_results.find().sort('timestamp', -1).limit(limit)` — Line 336
- **Read (by ID):** `db.rca_results.find_one({'_id': report_id})` — Line 357
- **Count:** `db.rca_results.count_documents({})` — Line 160

---

### 4.3 `metrics` Collection

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Auto-generated MongoDB ID |
| `timestamp` | DateTime | When metrics were captured |
| `cpu_usage` | Float | CPU usage percentage (0–100) |
| `memory_usage` | Float | Memory usage percentage (0–100) |
| `disk_usage` | Float | Disk usage percentage (0–100) |
| `response_time` | Float | Response time in milliseconds |
| `error_rate` | Float | Error rate percentage |
| `request_count` | Integer | Number of requests |
| `active_connections` | Integer | Active connections count |

**DAL Operations (in `app.py`):**
- **Read (history):** `db.metrics.find().sort('timestamp', -1).limit(limit)` — Line 427

---

### 4.4 `logs` Collection

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Auto-generated MongoDB ID |
| `timestamp` | DateTime | Log entry timestamp |
| `level` | String | Log level (`INFO`, `WARN`, `ERROR`, `CRITICAL`) |
| `message` | String | Log message content |
| `source` | String | Source component (e.g., `app-server`, `database`) |
| `host` | String | Server hostname |
| `process_id` | Integer | Process ID |

---

### 4.5 `alerts` Collection

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Auto-generated MongoDB ID |
| `id` / `alert_id` | String | Custom alert ID |
| `type` | String | Alert type (`CRITICAL_ANOMALY`, `THRESHOLD_BREACH`, etc.) |
| `severity` | String | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `message` | String | Alert message |
| `timestamp` | DateTime | When alert was triggered |
| `acknowledged` | Boolean | Whether alert has been acknowledged |
| `acknowledged_at` | String/DateTime | Acknowledgment timestamp |

**DAL Operations (in `app.py`):**
- **Read (all):** `db.alerts.find().sort('timestamp', -1).limit(50)` — Line 450
- **Update:** `db.alerts.update_one({'id': alert_id}, {'$set': {...}})` — Lines 475–481
- **Count:** `db.alerts.count_documents({})` — Line 507

---

## 5. Database Indexes (Performance Optimization)

**File:** [`arca-platform/seed.py`](../arca-platform/seed.py) — `create_indexes()` function (Lines 510–537)

```python
def create_indexes():
    # Anomalies indexes
    db.anomalies.create_index([('timestamp', -1)])
    db.anomalies.create_index([('severity', 1)])
    db.anomalies.create_index([('metric', 1)])

    # RCA results indexes
    db.rca_results.create_index([('timestamp', -1)])
    db.rca_results.create_index([('root_cause', 1)])
    db.rca_results.create_index([('confidence', -1)])

    # Metrics indexes
    db.metrics.create_index([('timestamp', -1)])

    # Logs indexes
    db.logs.create_index([('timestamp', -1)])
    db.logs.create_index([('level', 1)])
    db.logs.create_index([('source', 1)])

    # Alerts indexes
    db.alerts.create_index([('timestamp', -1)])
    db.alerts.create_index([('status', 1)])
    db.alerts.create_index([('severity', 1)])
```

---

## 6. DAL Code Components — Architecture Mapping

The DAL is implemented across several files in the backend:

```
arca-platform/backend/
├── app.py                          ← Main DAL entry point (connection + CRUD routes)
├── modules/
│   ├── anomaly_detector.py         ← Anomaly data model (Anomaly.to_dict() for DB storage)
│   ├── rca_engine.py               ← RCAResult data model for DB storage
│   ├── alert_system.py             ← Alert data model + notification logic
│   ├── log_collector.py            ← LogEntry model + file-based log collection
│   ├── metric_collector.py         ← MetricCollector for real-time system metrics
│   ├── event_correlator.py         ← CorrelatedEvent grouping for analysis
│   ├── recommendation_engine.py    ← Recommendation + Fix models
│   └── sliding_window.py           ← In-memory circular buffer (data caching)
├── .env / .env.example             ← DB connection configuration
└── requirements.txt                ← pymongo dependency
arca-platform/
└── seed.py                         ← Database seeding + index creation
```

### DAL Layer Flow

```
┌──────────────────────────────────────────────────────────┐
│  Presentation Layer (Flask REST API Routes in app.py)    │
│  GET /api/anomalies, POST /api/detect, etc.             │
└────────────────────────┬─────────────────────────────────┘
                         │  calls
┌────────────────────────▼─────────────────────────────────┐
│  Data Access Layer (DAL) — PyMongo operations in app.py  │
│  db.anomalies.find(), db.rca_results.insert_one(), etc.  │
└────────────────────────┬─────────────────────────────────┘
                         │  queries
┌────────────────────────▼─────────────────────────────────┐
│  MongoDB Database (arca_db)                              │
│  Collections: anomalies, rca_results, metrics,           │
│               logs, alerts                               │
└──────────────────────────────────────────────────────────┘
```

### Key DAL Operations Summary

| Operation | MongoDB Method | Location in `app.py` |
|---|---|---|
| **Insert One** | `db.collection.insert_one(doc)` | Lines 239, 251–257, 322 |
| **Insert Many** | `db.collection.insert_many(docs)` | `seed.py` Lines 173, 323, 366, 414, 506 |
| **Find All** | `db.collection.find(query)` | Lines 165, 204, 336, 427, 450 |
| **Find One** | `db.collection.find_one(filter)` | Lines 295, 357 |
| **Update One** | `db.collection.update_one(filter, update)` | Lines 475–481 |
| **Count Documents** | `db.collection.count_documents(filter)` | Lines 159–160, 505–511 |
| **Sort** | `.sort('field', -1)` | Lines 165, 204, 336, 427, 450 |
| **Limit** | `.limit(n)` | Lines 165, 204, 336, 427, 450 |
| **Create Index** | `db.collection.create_index(...)` | `seed.py` Lines 515–535 |
| **Delete Many** | `db.collection.delete_many({})` | `seed.py` Line 45 |

---

## 7. Data Models (Python Classes → MongoDB Documents)

### Anomaly → `anomalies` collection
```python
# modules/anomaly_detector.py
class Anomaly:
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.anomaly_type,
            'severity': self.severity,
            'value': self.value,
            'metric': self.metric_name,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description
        }
```

### RCAResult → `rca_results` collection
```python
# modules/rca_engine.py
@dataclass
class RCAResult:
    root_cause: str
    confidence: float
    affected_components: List[str]
    causal_chain: List[str]
    evidence: List[Dict]
    recommendations: List[str]
    timestamp: datetime
```

### Alert → `alerts` collection
```python
# modules/alert_system.py
@dataclass
class Alert:
    alert_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
```

---

## 8. Database Seeding Script

**File:** [`arca-platform/seed.py`](../arca-platform/seed.py)

The seed script populates all 5 collections with realistic test data:
- **23 anomalies** (CPU, Memory, Response Time, Error Rate, Log-based)
- **5 RCA reports** (Resource Exhaustion, Deployment Error, DB Connection, Memory Leak, Network Latency)
- **288 metric records** (24 hours of 5-minute interval data)
- **500 log entries** (mixed severity levels from various sources)
- **6 alerts** (various types and severities)

---

---

# Part B: White Box Testing & Black Box Testing [Marks = 10 + 10 = 20]

## Overview

- **White Box Testing (Glass Box Testing):** Tests where the tester has full knowledge of internal structure, code, and logic. Tests are designed based on code paths, branches, loops, and internal data structures.

- **Black Box Testing (Functional Testing):** Tests where the tester evaluates software without knowing its internal code. Tests are based on specifications, inputs, and expected outputs.

## Test Files

| File | Type | Description |
|---|---|---|
| `test_whitebox.py` | White Box | Unit tests covering internal logic, code branches, data structures |
| `test_blackbox.py` | Black Box | Functional tests covering API endpoints, input/output validation |

### Running the Tests

```bash
cd Assignment8

# Run White Box Tests
python -m pytest test_whitebox.py -v

# Run Black Box Tests
python -m pytest test_blackbox.py -v

# Run all tests
python -m pytest -v

# Run with coverage
python -m pytest --cov=. -v
```

---

## White Box Test Cases Summary

| # | Module Under Test | Test Case | What It Tests |
|---|---|---|---|
| WB-01 | AnomalyDetector | `test_init_valid_thresholds` | Constructor with valid dict input |
| WB-02 | AnomalyDetector | `test_init_invalid_thresholds` | Constructor rejects non-dict input |
| WB-03 | AnomalyDetector | `test_detect_log_anomalies_error_level` | ERROR level log detection branch |
| WB-04 | AnomalyDetector | `test_detect_log_anomalies_critical_level` | CRITICAL level log detection branch |
| WB-05 | AnomalyDetector | `test_detect_log_anomalies_deployment_keyword` | Deployment keyword matching in ERROR logs → CRITICAL |
| WB-06 | AnomalyDetector | `test_detect_log_anomalies_warning_keyword` | WARNING level with deployment keyword → MEDIUM |
| WB-07 | AnomalyDetector | `test_detect_log_anomalies_empty` | Empty list input returns empty |
| WB-08 | AnomalyDetector | `test_detect_metric_above_threshold` | Metric > max_value: threshold branch |
| WB-09 | AnomalyDetector | `test_detect_metric_below_threshold` | Metric < min_value: threshold branch |
| WB-10 | AnomalyDetector | `test_severity_calculation_critical` | Value >150% of threshold → CRITICAL |
| WB-11 | AnomalyDetector | `test_severity_calculation_high` | Value >125% of threshold → HIGH |
| WB-12 | AnomalyDetector | `test_severity_calculation_medium` | Value >110% of threshold → MEDIUM |
| WB-13 | AnomalyDetector | `test_severity_calculation_low` | Value just above threshold → LOW |
| WB-14 | AnomalyDetector | `test_statistical_detection` | Statistical Z-score detection with 10+ data points |
| WB-15 | AnomalyDetector | `test_is_anomaly_method` | `is_anomaly()` method logic |
| WB-16 | AnomalyDetector | `test_anomaly_history_tracking` | History append and limit retrieval |
| WB-17 | AnomalyDetector | `test_baseline_data_windowing` | Baseline data capped at 100 points |
| WB-18 | RCAEngine | `test_init_empty_rules` | Default rules loaded when empty list |
| WB-19 | RCAEngine | `test_analyze_empty_events` | No events → UNKNOWN result |
| WB-20 | RCAEngine | `test_rule_matching` | Rule pattern matching logic (types, metrics, keywords) |
| WB-21 | RCAEngine | `test_confidence_calculation` | Confidence scoring formula |
| WB-22 | RCAEngine | `test_causal_chain_generation` | Causal chain lookup by root cause |
| WB-23 | SlidingWindow | `test_buffer_eviction` | Deque maxlen eviction behavior |
| WB-24 | SlidingWindow | `test_metadata_tracking` | total_items_added, items_evicted counters |
| WB-25 | SlidingWindow | `test_invalid_max_size` | ValueError on max_size ≤ 0 |
| WB-26 | EventCorrelator | `test_time_window_grouping` | Anomalies grouped by time window correctly |
| WB-27 | EventCorrelator | `test_correlation_score_calculation` | Score factors: time, severity, dependencies |
| WB-28 | EventCorrelator | `test_minimum_anomalies_for_correlation` | < 2 anomalies = no correlation |
| WB-29 | RecommendationEngine | `test_priority_adjustment_high_confidence` | Confidence > 0.8 → priority upgrade |
| WB-30 | RecommendationEngine | `test_priority_adjustment_low_confidence` | Confidence < 0.5 → priority downgrade |
| WB-31 | AlertSystem | `test_alert_id_generation` | Unique alert ID format |
| WB-32 | AlertSystem | `test_acknowledge_updates_state` | Acknowledge sets flag and removes from queue |

---

## Black Box Test Cases Summary

| # | Feature | Test Case | Input | Expected Output |
|---|---|---|---|---|
| BB-01 | Anomaly Detection | Valid ERROR logs | List of ERROR log dicts | List of anomalies with severity ≥ HIGH |
| BB-02 | Anomaly Detection | Valid CRITICAL logs | List of CRITICAL log dicts | List of anomalies with severity = CRITICAL |
| BB-03 | Anomaly Detection | Normal metrics (within threshold) | `{cpu: 50, memory: 60}` | Empty list (no anomalies) |
| BB-04 | Anomaly Detection | Abnormal metrics (above threshold) | `{cpu: 95}` | Anomaly detected for cpu_usage |
| BB-05 | Anomaly Detection | Empty input | `[]` / `{}` | Empty list |
| BB-06 | Anomaly Detection | Mixed logs and metrics | Logs + metrics payload | Combined anomaly list |
| BB-07 | RCA Analysis | Deployment error anomalies | Deployment-related anomalies | Root cause = DEPLOYMENT_CONFIGURATION_ERROR |
| BB-08 | RCA Analysis | Resource anomalies | CPU + Memory anomalies | Root cause = RESOURCE_EXHAUSTION |
| BB-09 | RCA Analysis | No anomalies | Empty list | Root cause = UNKNOWN, confidence = 0.0 |
| BB-10 | RCA Analysis | Output structure validation | Any valid anomalies | Result has root_cause, confidence, recommendations |
| BB-11 | Recommendations | Known root cause | RESOURCE_EXHAUSTION | List of ≥ 3 prioritized recommendations |
| BB-12 | Recommendations | Unknown root cause | UNKNOWN_CAUSE | Generic recommendations returned |
| BB-13 | Recommendations | Sorting by priority | Any recommendations | HIGH before MEDIUM before LOW |
| BB-14 | Recommendations | Historical fix recording | Record + query | Fix recorded and retrievable |
| BB-15 | Alert System | Send alert | Alert data dict | Alert created with unique ID |
| BB-16 | Alert System | Acknowledge alert | Valid alert ID | acknowledged = True |
| BB-17 | Alert System | Acknowledge invalid ID | Non-existent ID | Returns False |
| BB-18 | Alert System | Filter by severity | Severity filter | Only matching alerts returned |
| BB-19 | Sliding Window | Add within capacity | 5 items to size-10 window | All 5 items available |
| BB-20 | Sliding Window | Add beyond capacity | 15 items to size-10 window | Only last 10 items remain |
| BB-21 | Sliding Window | Get recent N | Request 3 recent from 10 | Last 3 items returned |
| BB-22 | Event Correlator | Correlated events | Multiple anomalies in same time window | Grouped CorrelatedEvent |
| BB-23 | Event Correlator | Uncorrelated events | Anomalies in different time windows | Separate groups (or none if < 2 per window) |
| BB-24 | Log Collector | Parse valid log file | File with mixed log lines | Parsed entries with level, message, timestamp |
| BB-25 | Log Collector | Non-existent file | Invalid path | Empty list returned |
| BB-26 | Metric Collector | Get metric snapshot | System call | Dict with cpu_usage, memory_usage, disk_usage |
| BB-27 | Anomaly Model | `to_dict()` output | Anomaly object | Dict with all required keys |
| BB-28 | Full Pipeline | End-to-end: detect → correlate → RCA | Logs + metrics | Complete RCA result with recommendations |

---

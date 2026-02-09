# UML Class Diagram - Automated Root Cause Analysis Platform (ARCA)

**Part B, Q2 - CS331 Assignment 3**

This diagram shows the complete class structure for the Automated Root Cause Analysis Platform for Deployment Errors.

## System Architecture Overview

The system follows a pipeline architecture with the following layers:

1. **Data Collection Layer**: `LogCollector`, `MetricCollector`, `SlidingWindow`
2. **Analysis Layer**: `AnomalyDetector`, `EventCorrelator`
3. **Intelligence Layer**: `RCAEngine`, `RecommendationEngine`
4. **Presentation Layer**: `DashboardController`, `AlertSystem`
5. **Persistence Layer**: `DataStore`

---

## Complete UML Class Diagram

```mermaid
classDiagram
    class LogCollector {
        -string logFilePath
        -number lastReadPosition
        -number collectionInterval
        -boolean isRunning
        +constructor(logFilePath, interval)
        +startCollection() void
        +stopCollection() void
        +readNewLogs() Promise~LogEntry[]~
        +parseLogEntry(line) LogEntry
        -updateReadPosition() void
        -validateLogFile() boolean
    }
    
    class MetricCollector {
        -Map~string,number~ metrics
        -number collectionInterval
        -boolean isRunning
        +constructor(interval)
        +startCollection() void
        +stopCollection() void
        +collectCPUUsage() Promise~number~
        +collectMemoryUsage() Promise~number~
        +collectResponseTime() Promise~number~
        +getMetricSnapshot() MetricData
        -calculateAverages() void
    }
    
    class AnomalyDetector {
        -Map~string,Threshold~ thresholds
        -string detectionAlgorithm
        -Anomaly[] anomalyHistory
        +constructor(thresholds)
        +detectLogAnomalies(logs) Anomaly[]
        +detectMetricAnomalies(metrics) Anomaly[]
        +setThreshold(metric, threshold) void
        +isAnomaly(value, metric) boolean
        -applyStatisticalAnalysis(data) boolean
        -createAnomalyRecord(type, severity) Anomaly
    }
    
    class EventCorrelator {
        -number correlationWindow
        -CorrelatedEvent[] correlatedEvents
        -Map~string,string[]~ dependencyGraph
        +constructor(windowSize)
        +correlateAnomalies(anomalies) CorrelatedEvent[]
        +findRelatedEvents(anomaly) Anomaly[]
        +setDependencies(dependencies) void
        +isWithinTimeWindow(event1, event2) boolean
        -calculateCorrelationScore(events) number
        -groupByTimestamp(anomalies) Map
    }
    
    class RCAEngine {
        -CorrelatedEvent[] correlatedEvents
        -Rule[] rootCauseRules
        -RCAResult[] analysisHistory
        +constructor(rules)
        +analyzeRootCause(correlatedEvents) RCAResult
        +applyRule(rule, events) boolean
        +rankCauses(possibleCauses) string[]
        +generateCausalChain(rootCause) CausalChain
        -matchPattern(events, pattern) boolean
        -calculateConfidence(cause, events) number
    }
    
    class RecommendationEngine {
        -Map~string,Recommendation[]~ recommendationRules
        -Fix[] historicalFixes
        +constructor(rules)
        +generateRecommendations(rcaResult) Recommendation[]
        +prioritizeRecommendations(recommendations) Recommendation[]
        +getHistoricalFixes(rootCause) Fix[]
        +addNewRule(cause, recommendation) void
        -matchCauseToAction(cause) Recommendation[]
    }
    
    class SlidingWindow {
        -number windowSize
        -Array dataBuffer
        -number currentIndex
        +constructor(size)
        +addData(data) void
        +getData() Array
        +clear() void
        +isFull() boolean
        +getSize() number
        -removeOldest() void
    }
    
    class DashboardController {
        -DataStore dataStore
        -AlertSystem alertSystem
        +constructor(dataStore, alertSystem)
        +getSystemHealth(req, res) Promise~void~
        +getRCAReports(req, res) Promise~void~
        +getAnomalyHistory(req, res) Promise~void~
        +getRecommendations(req, res) Promise~void~
        +acknowledgeAlert(req, res) Promise~void~
        -formatResponse(data) object
    }
    
    class AlertSystem {
        -Alert[] alertQueue
        -string[] notificationChannels
        -string severityThreshold
        +constructor(channels, threshold)
        +sendAlert(anomaly, rootCause) Promise~void~
        +addChannel(channel) void
        +setThreshold(severity) void
        +getActiveAlerts() Alert[]
        -formatAlertMessage(anomaly) string
        -sendEmail(message) Promise~void~
    }
    
    class DataStore {
        -Database db
        -string location
        -boolean isConnected
        +constructor(location)
        +connect() Promise~void~
        +disconnect() Promise~void~
        +storeAnomaly(anomaly) Promise~void~
        +storeRCAResult(result) Promise~void~
        +getAnomalies(timeRange) Promise~Anomaly[]~
        +getRCAHistory() Promise~RCAResult[]~
        -createTables() Promise~void~
    }
    
    %% Relationships - Data Flow Pipeline
    LogCollector --> SlidingWindow : stores logs in
    MetricCollector --> SlidingWindow : stores metrics in
    SlidingWindow --> AnomalyDetector : provides data to
    AnomalyDetector --> EventCorrelator : sends anomalies to
    EventCorrelator --> RCAEngine : sends correlated events to
    RCAEngine --> RecommendationEngine : sends RCA results to
    RCAEngine --> AlertSystem : triggers alerts in
    
    %% Relationships - Storage & Display
    AnomalyDetector --> DataStore : persists anomalies to
    RCAEngine --> DataStore : persists RCA results to
    DashboardController --> DataStore : queries data from
    DashboardController --> AlertSystem : manages alerts in
    
    %% Cardinality Notes
    note for SlidingWindow "Maintains last N data points\\n(circular buffer)"
    note for AnomalyDetector "Single detector instance\\nprocesses all data streams"
    note for RCAEngine "Central analysis engine\\n(singleton pattern)"
    note for DataStore "Persistent storage\\nfor all analysis artifacts"
```

---

## Relationship Details

### Data Flow Chain (Analysis Pipeline)

1. **LogCollector → SlidingWindow**
   - Type: Association
   - Cardinality: 1 to 1
   - Description: LogCollector stores parsed log entries in sliding window buffer

2. **MetricCollector → SlidingWindow**
   - Type: Association
   - Cardinality: 1 to 1  
   - Description: MetricCollector stores performance metrics in sliding window

3. **SlidingWindow → AnomalyDetector**
   - Type: Association
   - Cardinality: 1 to 1
   - Description: Sliding window provides recent data points for anomaly detection

4. **AnomalyDetector → EventCorrelator**
   - Type: Association  
   - Cardinality: 1 to 1
   - Description: Detector sends identified anomalies for event correlation

5. **EventCorrelator → RCAEngine**
   - Type: Association
   - Cardinality: 1 to 1
   - Description: Correlator sends grouped related events for root cause analysis

6. **RCAEngine → RecommendationEngine**
   - Type: Association
   - Cardinality: 1 to 1
   - Description: RCA engine sends identified root causes for recommendation generation

7. **RCAEngine → AlertSystem**
   - Type: Association
   - Cardinality: 1 to 1
   - Description: Engine triggers alerts for critical issues requiring immediate attention

### Storage & Interface Layer

8. **AnomalyDetector → DataStore**
   - Type: Association
   - Cardinality: 1 to 1
   - Description: Detector persists all detected anomalies for historical tracking

9. **RCAEngine → DataStore**
   - Type: Association
   - Cardinality: 1 to 1
   - Description: Engine stores RCA results including root causes and evidence

10. **DashboardController → DataStore**
    - Type: Association
    - Cardinality: 1 to 1
    - Description: Controller queries datastore for historical data and reports

11. **DashboardController → AlertSystem**
    - Type: Association
    - Cardinality: 1 to 1
    - Description: Controller manages alert acknowledgments and notifications

---

## Design Patterns Used

1. **Pipeline Pattern**: Data flows through sequential processing stages from collection to analysis
2. **Singleton Pattern**: RCAEngine and DataStore ensure single instances
3. **Observer Pattern**: AlertSystem notifies subscribers when critical issues detected
4. **Repository Pattern**: DataStore abstracts data persistence layer
5. **Strategy Pattern**: AnomalyDetector supports multiple detection algorithms

---

## Key Design Decisions

1. **Sliding Window**: Maintains only recent data to optimize memory usage and focus on short-term trends
2. **Threshold + Statistical Hybrid**: Combines rule-based and statistical approaches for robust anomaly detection
3. **Event Correlation**: Groups related anomalies by time proximity to reduce noise
4. **Rule-Based RCA**: Uses predefined patterns for fast and explainable root cause identification
5. **Asynchronous Operations**: All data operations return Promises for non-blocking execution

---

*This diagram represents the core architecture of the Automated Root Cause Analysis Platform for detecting and diagnosing deployment errors.*

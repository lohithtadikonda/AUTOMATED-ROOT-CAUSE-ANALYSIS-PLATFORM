# 🔍 Automated Root Cause Analysis Platform (ARCA)

## 📌 1. Introduction

### 1.1 Purpose
The purpose of this project is to develop an **Automated Root Cause Analysis Platform**. This system is designed to automatically identify the root cause of system failures by continuously monitoring logs, metrics, and system events. It aims to reduce the reliance on human expertise and manual troubleshooting.

### 1.2 Scope
In modern software systems, failures often occur due to multiple interconnected issues. This project automates the RCA process by:
* **Continuously monitoring** logs and metrics.
* **Detecting anomalies** automatically.
* **Correlating** related failures.
* **Identifying** the root cause.
* **Suggesting** corrective actions.

---

## 📖 2. Definitions & Acronyms

| Term | Description |
| :--- | :--- |
| **RCA** | Root Cause Analysis |
| **Anomaly** | Deviation from normal system behavior |
| **Metric** | Quantitative system performance data (CPU, RAM, etc.) |
| **Log** | Record of system or application events |
| **Sliding Window** | Fixed-size recent data set used for analysis |

---

## ⚙️ 3. Overall Description

### 3.1 Product Functions
The system performs the following core functions:
1.  **Continuous Data Collection:** Ingests logs and performance metrics.
2.  **Anomaly Detection:** Uses statistical thresholds to find abnormal behavior.
3.  **Event Correlation:** Links multiple anomalies based on timestamps.
4.  **Root Cause ID:** Pinpoints the origin of the failure.
5.  **Recommendation Engine:** Suggests fixes to the IT Engineer.
6.  **Visualization:** Displays health and reports on a Web Dashboard.

### 3.2 User Classes
* **System Administrator:** Monitors system health and views RCA reports.
* **IT Engineer:** Uses analysis results to resolve failures.
* **Project Evaluator:** Reviews system design and output.

### 3.3 Operating Environment
* **OS:** Windows or Linux
* **Language:** Python (Recommended) or Java
* **Database:** MySQL or SQLite
* **Interface:** Web Browser (Chrome, Firefox, Edge)

---

## 🚀 4. System Features

* **Continuous Data Collection:** Fetches data at fixed intervals; reads only new data to avoid duplication.
* **Log & Metric Monitoring:** Extracts errors/warnings and tracks CPU, Memory, Response Time, etc.
* **Sliding Window Management:** Maintains recent data to analyze short-term trends.
* **Anomaly Detection:** Uses threshold-based and statistical techniques.
* **Event Correlation Engine:** Correlates anomalies based on time and dependency.
* **Recommendation Engine:** Generates corrective actions based on predefined rules.
* **Alert System:** Critical issues trigger immediate notifications.

---

## 📋 5. Functional Requirements

### Data Processing
* **FR1:** The system shall continuously collect logs and metrics at predefined intervals.
* **FR2:** The system shall read only newly added log entries.
* **FR3:** The system shall process CPU, memory, response time, and error metrics.
* **FR4:** The system shall maintain recent data in a sliding window.

### Analysis & Core Logic
* **FR5:** The system shall detect abnormal behavior automatically.
* **FR6:** The system shall correlate multiple anomalies occurring within the same time window.
* **FR7:** The system shall identify the most probable root cause.
* **FR8:** The system shall suggest corrective actions.

### User Interface
* **FR9:** The system shall display analysis results through a web dashboard.
* **FR10:** The system shall notify users when critical failures occur.

---

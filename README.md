DONE BY PRIYANSHU KUMAR (2301163)


#  Automated Root Cause Analysis Platform (ARCA)



##  1. Introduction

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

##  2. Definitions & Acronyms

| Term | Description |
| :--- | :--- |
| **RCA** | Root Cause Analysis |
| **Anomaly** | Deviation from normal system behavior |
| **Metric** | Quantitative system performance data (CPU, RAM, etc.) |
| **Log** | Record of system or application events |
| **Sliding Window** | Fixed-size recent data set used for analysis |

---

##  3. Overall Description

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
* **Language:** Python,Java
* **Database:** MongoDB
* **Interface:** Web Browser (Chrome, Firefox, Edge)

---

##  4. System Features

* **Continuous Data Collection:** Fetches data at fixed intervals; reads only new data to avoid duplication.
* **Log & Metric Monitoring:** Extracts errors/warnings and tracks CPU, Memory, Response Time, etc.
* **Sliding Window Management:** Maintains recent data to analyze short-term trends.
* **Anomaly Detection:** Uses threshold-based and statistical techniques.
* **Event Correlation Engine:** Correlates anomalies based on time and dependency.
* **Recommendation Engine:** Generates corrective actions based on predefined rules.
* **Alert System:** Critical issues trigger immediate notifications.

---

##  5. Functional Requirements

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

##  6. Non-Functional Requirements

* **Performance:** Processing and detection must occur within acceptable time limits.
* **Reliability:** The system must operate continuously without crashing.
* **Scalability:** Efficient handling of increasing log/metric volume.
* **Maintainability:** Modular code structure for easy updates.
* **Usability:** User-friendly dashboard for non-experts.
* **Security:** Prevention of unauthorized access to sensitive log data.

---

##  7. System Architecture

### High-Level Flow
1.  **Monitoring Module:** Collects Log & Metric Data.
2.  **Analysis Module:**
    * *Anomaly Detector* (Finds deviations)
    * *Correlator* (Links events)
    * *RCA Engine* (Decides cause)
3.  **Visualization Module:** Dashboard & Alerting.

### Data Requirements
* **Logs:** Text-based entries with timestamps.
* **Metrics:** Numeric values with timestamps.

---

##  8. Limitations & Assumptions

* **Accuracy:** Dependent on the quality of input logs and metrics.
* **Rule-Based:** Detection is limited to predefined rules and thresholds.
* **Resource Constraints:** Designed to work on limited hardware for academic/testing purposes.
* **Assumption:** It is assumed that logs are available or can be simulated in the environment.

---

##  9. Deployment Architecture

### 9.1 Technology Stack

**Backend (AWS EC2):**
* **Platform:** AWS EC2 (t3.medium: 2 vCPU, 4GB RAM)
* **Operating System:** Ubuntu 22.04 LTS
* **Runtime:** Python 3.11+
* **Framework:** Flask 3.0 or FastAPI
* **WSGI Server:** Gunicorn (4 workers)
* **Reverse Proxy:** Nginx
* **Process Manager:** Systemd

**Frontend (Vercel):**
* **Platform:** Vercel (Serverless with CDN)
* **Framework:** React 18 + Vite
* **UI Library:** Material-UI
* **Build Tool:** Vite
* **API Client:** Axios

**Database:**
* **Provider:** MongoDB Atlas (Cloud)
* **Tier:** M0 Free / M10 Production
* **Features:** 3-node replica set, automated backups

**CI/CD:**
* **Platform:** GitHub Actions
* **Features:** Automated testing, deployment, health checks

### 9.2 Deployment Topology

```
Users → Vercel (Frontend) → AWS EC2 (Backend) → MongoDB Atlas (Database)
                ↓
         GitHub Actions (CI/CD)
```

### 9.3 Why This Architecture?

✅ **Scalability:** Independent scaling of frontend and backend  
✅ **Performance:** Vercel CDN for global content delivery  
✅ **Cost-Effective:** Free tier options, pay-as-you-grow  
✅ **Reliability:** Managed services with high availability  
✅ **Security:** HTTPS, VPC, security groups, JWT authentication  
✅ **Developer Experience:** Automated deployments with git push  

---

##  10. Project Structure

```
LAB_Software/
├── README.md
├── Assignment3/
│   ├── COMPLETION_SUMMARY.md
│   ├── diagrams/
│   │   └── uml_class_diagram.md
│   └── implementations/
│       ├── AnomalyDetector.py
│       ├── RCAEngine.py
│       └── IMPLEMENTATION_GUIDE.md
├── Assignment4/
│   └── Assignment4_Solution.md
├── Assignment5/
│   ├── Assignment5_Solution.md
│   ├── COMPLETION_SUMMARY.md
│   └── deployment-scripts/
│       ├── setup_ec2.sh
│       ├── deploy.sh
│       └── README.md
└── Assignments/ (reference materials)
```

---

##  11. Assignments Completed

### Assignment 3: UML Design & Implementation ✅
- **Part A:** Requirements analysis
- **Part B:** UML class diagrams (10 classes with relationships)
- **Part C:** Implementation of AnomalyDetector and RCAEngine modules
- **Status:** Complete with comprehensive documentation

### Assignment 4: Software Architecture Analysis ✅
- **Architecture Selected:** Layered (N-Tier) Architecture
- **Components Identified:** 10 major components across 5 layers
- **Justification:** Detailed analysis of maintainability, scalability, performance
- **Status:** Complete with architecture diagrams

### Assignment 5: Deployment and DevOps ✅
- **Cloud Platform:** AWS EC2 + Vercel + MongoDB Atlas
- **CI/CD Pipeline:** GitHub Actions automation
- **Documentation:** 50+ page deployment guide
- **Scripts:** Automated setup and deployment scripts
- **Security:** SSL/TLS, authentication, rate limiting
- **Monitoring:** CloudWatch, logging, health checks
- **Status:** Production-ready deployment architecture

---

##  12. Quick Start Guide

### Development Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/arca-platform.git
cd arca-platform

# Backend setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run dev

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Run Tests

```bash
# Backend tests
python Assignment3/implementations/AnomalyDetector.py
python Assignment3/implementations/RCAEngine.py

# Run all tests
pytest tests/ -v
```

### Deploy to Production

See [Assignment5/Assignment5_Solution.md](Assignment5/Assignment5_Solution.md) for complete deployment guide.

---

##  13. Key Features Implemented

✅ **Anomaly Detection**
- Threshold-based detection (CPU > 80%, Memory > 85%)
- Statistical analysis (mean + 2σ standard deviation)
- Log-level based detection (ERROR, CRITICAL)
- Deployment error keyword matching

✅ **Root Cause Analysis**
- Rule-based pattern matching
- Confidence scoring (0.0-1.0)
- Causal chain generation
- Evidence collection
- Automated recommendations

✅ **Deployment Infrastructure**
- AWS EC2 backend hosting
- Vercel frontend CDN
- MongoDB Atlas database
- Automated CI/CD pipeline
- SSL/TLS security
- Health monitoring

---

##  14. Documentation

| Document | Location | Description |
|----------|----------|-------------|
| **System Overview** | README.md | This file - project introduction |
| **UML Diagrams** | Assignment3/diagrams/ | Class diagrams and relationships |
| **Implementation Guide** | Assignment3/implementations/ | AnomalyDetector & RCAEngine code |
| **Architecture Analysis** | Assignment4/Assignment4_Solution.md | Layered architecture justification |
| **Deployment Guide** | Assignment5/Assignment5_Solution.md | Complete deployment documentation |
| **Scripts** | Assignment5/deployment-scripts/ | Automated setup scripts |

---

##  15. Performance Specifications

| Metric | Target | Notes |
|--------|--------|-------|
| API Response Time | < 200ms | Average for detection endpoint |
| Frontend Load Time | < 2 seconds | Initial page load |
| Database Query Time | < 50ms | Average query latency |
| Anomaly Detection | Real-time | Within 1 minute of occurrence |
| Concurrent Users | 100-500 | With t3.medium instance |
| Uptime | 99.5%+ | With proper monitoring |

---

##  16. Security Features

* **Transport Security:** SSL/TLS encryption on all connections
* **Authentication:** JWT token-based authentication
* **Authorization:** Role-based access control
* **Network Security:** AWS Security Groups, VPC isolation
* **Application Security:** Input validation, rate limiting, CORS
* **Secrets Management:** Environment variables, no hard-coded credentials
* **Database Security:** Encrypted connections, IP whitelisting

---

##  17. Cost Estimates

### Development Environment
- **Monthly Cost:** ~$15
- **Components:** EC2 t3.small, MongoDB M0 (free), Vercel Hobby (free)

### Production Environment (Small Scale)
- **Monthly Cost:** ~$232
- **Components:** EC2 t3.medium, MongoDB M10, Vercel Pro, data transfer

### Production Environment (Medium Scale)
- **Monthly Cost:** ~$442
- **Components:** EC2 t3.large, MongoDB M20, enhanced features

See [Assignment5/Assignment5_Solution.md](Assignment5/Assignment5_Solution.md) for detailed cost breakdown.

---

##  18. Future Enhancements

* **Machine Learning:** Replace rule-based detection with ML models
* **Auto-Scaling:** Implement horizontal scaling with load balancers
* **Multi-Region:** Deploy across multiple AWS regions
* **Advanced Monitoring:** Integrate with Datadog or New Relic
* **Mobile App:** iOS/Android app for alerts and monitoring
* **Kubernetes:** Containerized deployment with K8s orchestration
* **Real-time Updates:** WebSocket-based live dashboard

---

##  19. Contributing

This is an academic project for CS331 Software Engineering Lab. For questions or suggestions:

1. Review the documentation in each assignment folder
2. Check troubleshooting guides
3. Refer to inline code comments
4. Contact the development team

---

##  20. License & Acknowledgments

**Course:** CS331 - Software Engineering Lab  
**Institution:** [Your Institution Name]  
**Year:** 2026  

**Technologies Used:**
- Python, Flask, React, MongoDB
- AWS (EC2, S3, CloudWatch)
- Vercel, GitHub Actions
- Nginx, Gunicorn, Systemd

**References:**
- AWS Documentation
- MongoDB Atlas Documentation
- Vercel Documentation
- Flask Documentation
- React Documentation

---

**Project Status:** ✅ Complete and Production-Ready  
**Last Updated:** February 17, 2026  
**Version:** 1.0.0



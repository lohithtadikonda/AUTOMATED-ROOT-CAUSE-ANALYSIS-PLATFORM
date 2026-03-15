# Assignment 6 - User Interface Design and Implementation

**Course**: CS331 (Software Engineering Lab)  
**Project**: ARCA Platform (Automated Root Cause Analysis)  

---

## I. UI Type Selection and Justification

### Selected UI Type
A **hybrid UI** is used in ARCA:
- **Menu-based interface** for module navigation
- **Direct manipulation interface** for real-time monitoring interactions

### Why this UI is appropriate for ARCA

1. **Supports multi-module workflows**  
   ARCA has multiple functional modules: Dashboard, System Health, Anomalies, RCA Reports, and Alerts. A menu-based navigation structure allows quick movement between modules and clear task separation.

2. **Improves operator efficiency**  
   Monitoring and incident-response systems require fast actions. Direct manipulation elements such as refresh buttons, filters, row selection, and detail panels allow users to inspect and act without complex command inputs.

3. **Fits real-time operations**  
   ARCA is used for live system monitoring. Interactive controls for refresh and filtering make it suitable for changing operational states.

4. **High usability and learnability**  
   The hybrid pattern reduces learning effort for new users while retaining power features for advanced users.

5. **Scalable for future enhancements**  
   The design can be extended to include additional pages, controls, and workflows without changing the fundamental interaction model.

### Conclusion
The chosen hybrid UI is the best fit because ARCA needs both structured navigation and high-interaction workflows for real-time anomaly management and root cause investigation.

---

## II. UI Code Implementation and User Interactions (10 Marks)

### Implementation Area
All UI components were implemented and enhanced inside:

- `arca-platform/frontend/src/App.css`
- `arca-platform/frontend/src/pages/Dashboard.jsx`
- `arca-platform/frontend/src/pages/Alerts.jsx`
- `arca-platform/frontend/src/pages/Anomalies.jsx`
- `arca-platform/frontend/src/pages/RCAReports.jsx`
- `arca-platform/frontend/src/pages/SystemHealth.jsx`
- `arca-platform/frontend/src/pages/Alerts.css`
- `arca-platform/frontend/src/pages/Anomalies.css`
- `arca-platform/frontend/src/pages/RCAReports.css`

### Implemented Interactions

#### 1. Dashboard interactions
- Manual refresh button added
- Auto-refresh retained (30s)
- Last updated timestamp shown
- Recent data list-size filter (5/10/20)
- Statistics and metrics update on refresh/filter changes

#### 2. Alerts interactions
- Manual refresh button added
- Alert acknowledgment with action feedback
- Alert dismissal from current view
- View Details action with dedicated detail panel
- Action status banners for success/error

#### 3. Anomalies interactions
- Severity filter retained and improved usage flow
- Search box added (severity/type/metric/description)
- Clickable anomaly rows
- Detailed anomaly inspection panel
- Live filtered results count

#### 4. RCA Reports interactions
- Confidence-based filtering (All/High/Medium/Low)
- Search by root cause/component
- View Details interaction to open selected report panel
- Recommendations, causal chain, and components shown in detail view

#### 5. System Health interactions
- Manual refresh button added
- Auto-refresh toggle added
- Last updated timestamp shown
- Real-time metrics and status cards continue to update

### Build and Validation
Frontend was validated successfully using production build:

```bash
cd arca-platform/frontend
npm run build
```

Build result: **Success** (Vite build completed without errors).

---

## User Interaction Demonstration

Perform and capture the following interactions for evaluation:

1. Navigate between all menu pages from the top navigation.
2. On Dashboard, change list size and click Refresh.
3. On Alerts, open View Details, click Acknowledge, and Dismiss one alert.
4. On Anomalies, apply severity filter, search text, and click a row to open details.
5. On RCA Reports, apply confidence filter, search, and open View Details.
6. On System Health, toggle auto-refresh and click Refresh now.

Recommended evidence:
- Minimum 5 screenshots (one per page)
- Optional short video/GIF showing end-to-end interaction flow

---

## Submission Checklist

- [x] Part I UI choice and justification completed
- [x] Part II UI components implemented in project code
- [x] Interactive user actions implemented across pages
- [x] Frontend build validated successfully
- [ ] Screenshots/video evidence attached

---

## Final Remarks
The ARCA frontend now demonstrates both required assignment aspects:
- A justified UI style selection
- A complete interactive implementation with user-visible actions and state updates

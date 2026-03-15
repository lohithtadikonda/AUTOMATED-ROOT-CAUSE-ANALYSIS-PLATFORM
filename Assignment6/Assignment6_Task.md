# CS331 Software Engineering Lab - Assignment 6 Task File

**Course**: CS331 (Software Engineering Lab)  
**Assignment**: 6  
**Total Marks**: 20  
**Project**: ARCA Platform (Automated Root Cause Analysis)

---

## Assignment Requirements (From PDF)

### Part I (10 Marks)
Choose an appropriate User Interface (UI) style for the software engineering project and justify the choice.

Examples:
- Command-language based interface
- Menu-based interface
- Direct manipulation interface
- Form-based interface
- Hybrid interface

### Part II (10 Marks)
Implement the UI code components and demonstrate user interactions with the software.

---

## Selected UI Type for ARCA Platform

**Chosen UI**: Hybrid of Menu-Based + Direct Manipulation Interface

### Why this is appropriate
- ARCA has multiple workflows (Dashboard, Alerts, Anomalies, RCA Reports, System Health), so menu-based navigation is needed for clarity.
- Users need to interact with data visualizations, filters, and actions (view anomaly details, open RCA report, refresh health), which fits direct manipulation.
- This combination supports both discoverability (through menu/navigation) and efficiency (through interactive controls).
- It matches real-world monitoring tools where operators both navigate modules and interact directly with charts/tables.

---

## Implementation Scope in Existing Project

Work inside:
- `arca-platform/frontend/src/components/`
- `arca-platform/frontend/src/pages/`
- `arca-platform/frontend/src/services/`
- `arca-platform/frontend/src/App.jsx`

Already available pages:
- Dashboard
- Alerts
- Anomalies
- RCAReports
- SystemHealth

---

## Task Breakdown

## 1. Navigation and Menu-Based UI
- Ensure `Navbar.jsx` provides clear menu items for all major modules.
- Highlight active route/page.
- Keep menu labels user-friendly.

**Expected output**:
- Smooth navigation between all pages without broken routes.

## 2. Direct Manipulation UI Components
Implement/verify interactive elements on each page:
- Dashboard: cards/charts update on refresh or filter.
- Alerts: acknowledge/dismiss/view details actions.
- Anomalies: severity filter, search, click row/card for details.
- RCA Reports: select report and open detailed view.
- System Health: live status view and refresh controls.

**Expected output**:
- User can interact directly with data and immediately see visual/state changes.

## 3. API Integration for User Interaction
- Wire UI actions with `services/api.js` endpoints.
- Handle loading, success, and error states.
- Show empty states when no data is available.

**Expected output**:
- Frontend actions are connected to backend responses in a user-friendly way.

## 4. UI Quality and Usability Improvements
- Add consistent spacing, typography, and color hierarchy.
- Keep responsive layout for desktop and mobile widths.
- Ensure buttons, tables, and cards are readable and accessible.

**Expected output**:
- Polished interface that is easy to use and explain in lab evaluation.

## 5. Interaction Demonstration Evidence
Prepare proof of interactions:
- Screenshots (minimum 5): one per major page.
- Optional short screen recording/GIF showing navigation + interactions.
- Note each interaction performed.

---

## Deliverables for Submission

1. UI Justification write-up (Part I)
2. Updated frontend code (Part II)
3. Interaction evidence (screenshots/GIF)
4. Final report file: `Assignment6_Solution.md` (to be created after implementation)

---

## Evaluation Checklist (Self-Check)

- [ ] UI type selected and justified clearly
- [ ] Menu-based navigation works across all pages
- [ ] Direct manipulation interactions implemented
- [ ] API-connected interactions handled with proper states
- [ ] No major UI break on responsive view
- [ ] User interaction evidence prepared
- [ ] Ready to compile final `Assignment6_Solution.md`

---

## Execution Plan (What we do next)

1. Implement missing UI interactions in `arca-platform/frontend`.
2. Test user flows page by page.
3. Capture screenshots of final interactions.
4. Create `Assignment6_Solution.md` with:
   - Part I justification
   - Part II implementation details
   - Evidence references

---

## Notes

- Keep changes aligned with existing ARCA frontend style.
- Prefer reusable components where possible.
- If backend API is unavailable for any action, mock the UI state transition and document it in final solution.

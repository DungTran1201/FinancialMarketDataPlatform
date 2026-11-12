# UX Screen Specification — `[TEMPLATE]`

| Document Metadata | Value |
|---|---|
| **Document ID** | `UX-SCR-[NNN]` |
| **Title** | `[TO BE COMPLETED]` |
| **Version** | `0.1.0` |
| **Status** | `DRAFT` (`[PROPOSED — NOT APPROVED]`) |
| **Authoring Role** | `ux-modeler` |
| **Review Role** | `requirements-engineer` |
| **Created Date** | `YYYY-MM-DD` |
| **Updated Date** | `YYYY-MM-DD` |
| **Work Item Reference** | `work-items/[WORK-ITEM-ID]/` |
| **Canonical Model Reference** | `models/ux/ux.yaml` |
| **Source References** | `[TO BE COMPLETED]` |

---

## 1. Purpose `[MANDATORY]`

Specifies a single screen (`SCR-###`) including route, user roles, purpose, UI components, data dependencies (`API-###`), user actions, states (`Loading`, `Empty`, `Fresh`, `Stale`, `Error`), navigation, responsive behavior, accessibility, and error handling.

---

## 2. Scope & Boundaries `[MANDATORY]`

Applies to `docs/product/11-ux/` and feature packages under `docs/features/`.

---

## 3. Screen Identification & Access `[MANDATORY]`

- **Screen ID**: `SCR-[NNN]`
- **Route**: `/[route-path]`
- **Authorized User Roles**: `[viewer|analyst|operator|admin]`
- **Purpose**: `[TO BE COMPLETED]`

---

## 4. UI Component Breakdown & Data Dependencies `[MANDATORY]`

| Component ID | UI Element | Data Source (`API-###` / WS Stream) | Refresh / Freshness Policy |
|---|---|---|---|

---

## 5. User Actions, Events & Navigation `[MANDATORY]`

| Action | Trigger Element | Target `API-###` or Route | Validation / Confirmation |
|---|---|---|---|

---

## 6. Screen States (`Loading`, `Empty`, `Fresh`, `Stale Data`, `Error`) `[MANDATORY]`

- **Loading State**: `[TO BE COMPLETED]`
- **Empty State**: `[TO BE COMPLETED]`
- **Stale Market Data Indicator (`is_stale=true`)**: `[TO BE COMPLETED]`
- **Error State & Retry**: `[TO BE COMPLETED]`

---

## 7. Responsive Behavior & Accessibility (WCAG) `[MANDATORY]`

- **Responsive Breakpoints**: `[TO BE COMPLETED]`
- **Keyboard & Screen Reader Accessibility**: `[TO BE COMPLETED]`

---

## 8. Assumptions `[MANDATORY]`

- **ASSUMP-01**: `[ASSUMPTION — REQUIRES VALIDATION]`

---

## 9. Open Questions `[MANDATORY]`

- **OQ-01**: `[OPEN QUESTION]`

---

## 10. Dependencies `[MANDATORY]`

- **Upstream Dependencies**: `[TO BE COMPLETED]`
- **Downstream Consumers**: `[TO BE COMPLETED]`

---

## 11. Bidirectional Traceability `[MANDATORY]`

| Upstream Artifact ID | Current Artifact ID | Downstream Artifact ID | Verification Reference |
|---|---|---|---|
| `[TO BE COMPLETED]` | `UX-SCR-[NNN]` | `[TO BE COMPLETED]` | `[TO BE COMPLETED]` |

---

## 12. Approval & Baseline Sign-Off `[CONDITIONAL]`

| Reviewer Role | Reviewer Name / Agent | Review Decision | Date | Evidence / Notes |
|---|---|---|---|---|
| `requirements-engineer` | `[TO BE COMPLETED]` | `[PROPOSED — NOT APPROVED]` | `YYYY-MM-DD` | `[TO BE COMPLETED]` |

# Detailed Endpoint API Contract — `[TEMPLATE]`

| Document Metadata | Value |
|---|---|
| **Document ID** | `API-CTR-[NNN]` |
| **Title** | `[TO BE COMPLETED]` |
| **Version** | `0.1.0` |
| **Status** | `DRAFT` (`[PROPOSED — NOT APPROVED]`) |
| **Authoring Role** | `api-architect` |
| **Review Role** | `security-reviewer` |
| **Created Date** | `YYYY-MM-DD` |
| **Updated Date** | `YYYY-MM-DD` |
| **Work Item Reference** | `work-items/[WORK-ITEM-ID]/` |
| **Canonical Model Reference** | `models/api/api.yaml` |
| **Source References** | `[TO BE COMPLETED]` |

---

## 1. Purpose `[MANDATORY]`

Specifies a single endpoint contract (`API-###`) including method, path, purpose, RBAC, request/response schemas, error codes, validation, idempotency, timeout, rate limit, and related Use Cases.

---

## 2. Scope & Boundaries `[MANDATORY]`

Applies to `docs/product/08-api/` and feature packages under `docs/features/`.

---

## 3. Endpoint Identification & Security `[MANDATORY]`

- **API ID**: `WEB-API-[NNN]`
- **Method & Path**: `[GET|POST|PUT|DELETE] /api/v1/[path]`
- **Purpose**: `[TO BE COMPLETED]`
- **Authorization / RBAC Role**: `[viewer|analyst|operator|admin]`
- **Idempotency Policy**: `[Safe Read | Idempotency-Key Required]`
- **Hard Timeout & Rate Limit**: `[Timeout ms | req/min]`

---

## 4. Request Schema (Path, Query, Headers, JSON Body) `[MANDATORY]`

```json
{
  "_comment": "[TO BE COMPLETED]"
}
```

---

## 5. Response Schema (`200 OK` / `202 Accepted`) `[MANDATORY]`

```json
{
  "data": {},
  "meta": {
    "request_id": "[TO BE COMPLETED]",
    "source": "[TO BE COMPLETED]",
    "is_stale": false
  }
}
```

---

## 6. Validation Rules & Error Model (`400`, `401`, `403`, `422`, `429`, `503`) `[MANDATORY]`

| HTTP Status | Error Code | Trigger Condition | Client Recovery Action |
|---|---|---|---|

---

## 7. Related Use Cases (`UC-###`) & Requirements (`FR-###`) `[MANDATORY]`

- **Use Cases**: `[TO BE COMPLETED]`
- **Requirements**: `[TO BE COMPLETED]`

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
| `[TO BE COMPLETED]` | `API-CTR-[NNN]` | `[TO BE COMPLETED]` | `[TO BE COMPLETED]` |

---

## 12. Approval & Baseline Sign-Off `[CONDITIONAL]`

| Reviewer Role | Reviewer Name / Agent | Review Decision | Date | Evidence / Notes |
|---|---|---|---|---|
| `security-reviewer` | `[TO BE COMPLETED]` | `[PROPOSED — NOT APPROVED]` | `YYYY-MM-DD` | `[TO BE COMPLETED]` |

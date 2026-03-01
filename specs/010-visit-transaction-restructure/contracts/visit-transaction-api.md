# API Contract: Visit Status Transition

**Endpoint**: `PATCH /api/v1/visits/{visit_id}/status/`

## Request

```json
{
  "status": "pending_nurse"
}
```

### Valid Status Values

`pending_agency`, `pending_nurse`, `accepted`, `en_route`, `in_progress`, `completed`, `cancelled`

## Response (200 OK)

```json
{
  "id": "uuid",
  "status": "pending_nurse",
  "updated_at": "2026-03-01T20:00:00Z"
}
```

## Error Response (400 Bad Request)

```json
{
  "detail": "لا يمكن الانتقال من \"pending_agency\" إلى \"completed\".",
  "code": "invalid_transition"
}
```

## Transition Rules

Enforced by `ALLOWED_TRANSITIONS` map. See `data-model.md` for full transition table.

---

# API Contract: Transaction Auto-Calculation

**Trigger**: Transaction `save()` — not a direct API endpoint.

## Behavior

When a `Transaction` is saved:

1. `agency_payout = amount_paid * Decimal('0.85')` is computed automatically
2. If `status == SETTLED` and `settled_at` is null, `settled_at = now()` is set
3. `agency_payout` is never editable via admin or API

## Input Fields

| Field              | Type          | Required | Default  |
| ------------------ | ------------- | -------- | -------- |
| `visit`            | UUID          | Yes      | —        |
| `agency`           | UUID          | Yes      | —        |
| `amount_paid`      | Decimal(10,2) | Yes      | —        |
| `wateen_take_rate` | Decimal(5,2)  | No       | 15.00    |
| `status`           | String        | No       | ESCROWED |

## Computed Fields (output only)

| Field           | Calculation                                  |
| --------------- | -------------------------------------------- |
| `agency_payout` | `amount_paid * (1 - wateen_take_rate / 100)` |
| `settled_at`    | Auto-set on transition to `SETTLED`          |

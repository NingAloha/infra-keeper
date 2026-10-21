# Service — [service-name]

| Field | Documented value |
| --- | --- |
| Purpose | `[user-facing purpose]` |
| Owner | `[person or team]` |
| Dependencies | `[device, storage, upstream, or route records]` |
| Exposure | `[internal, public through documented ingress, or unknown]` |
| Health signal | `[observable success condition]` |
| Recovery reference | `[runbook or approved recovery path]` |
| Secrets | `[secret manager owner/location, never values]` |

## Change constraints

- Shared ports, routes, or resources: `[known constraints or unknown]`
- Validation path: `[what must succeed after a change]`
- Rollback trigger and action: `[safe reversal]`

## Evidence boundary

Documented on `[YYYY-MM-DD]`. This record is not evidence of current process health.

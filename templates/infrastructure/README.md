# Infrastructure inventory

> Baseline only. Last reviewed: [YYYY-MM-DD]. Live state must be verified when it matters.

## Assets

| Asset | Role | Record | Owner | Evidence boundary |
| --- | --- | --- | --- | --- |
| `[device-name]` | `[purpose]` | `devices/[device-name]/README.md` | `[owner/team]` | `[last review or live check]` |

## Service relationships

Describe dependencies in plain language. Example: `[public entry] → [ingress] → [service] → [data dependency]`.

## Documentation conventions

- Keep secrets in `[secret manager]`; do not record values here.
- Label records as documented baseline, user report, live observation, or unknown.
- Put changes and recovery evidence in each device's `operations.md`.

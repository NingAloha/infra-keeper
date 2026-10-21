# Routing ownership

> Document names and owners, not tokens, private keys, or provider credentials.

| Name or route | Ingress owner | Target service | TLS/certificate owner | Last verified |
| --- | --- | --- | --- | --- |
| `[service.example]` | `[device or provider]` | `[service record]` | `[owner/runbook]` | `[YYYY-MM-DD]` |

## Change guardrails

- Confirm name ownership and existing routes before adding an ingress rule.
- Document the rollback target before changing DNS, proxy, or firewall configuration.
- Treat a successful configuration write as incomplete until the intended request path is verified.

# Infrastructure repository guide

## Recommended shape

Use a small root inventory plus focused records. The exact names are flexible; the relationship is more important than the tree.

```text
README.md                         inventory and service relationships
devices/<device>/README.md        landing page and index for one device
devices/<device>/system.md        operating system, capacity, lifecycle
devices/<device>/network.md       interfaces, exposure, firewall ownership
devices/<device>/services/*.md    service purpose and dependencies
devices/<device>/operations.md    evidence, maintenance, recovery notes
domains/routing.md                DNS and ingress ownership across devices
```

## What each record should answer

| Record | Questions it should answer |
| --- | --- |
| Root README | Which assets exist? What depends on what? Which records are authoritative? |
| Device README | What is this device for? Which documents and related systems matter? |
| System | What platform, capacity limits, backup/lifecycle constraints, and evidence date apply? |
| Network | What traffic is expected, who owns the firewall or ingress, and what is intentionally not exposed? |
| Service record | What does it do, who owns it, what does it depend on, and how is it verified or recovered? |
| Routing | Which name maps to which ingress owner and service, without storing secrets? |
| Operations | What was changed, why, how it was checked, and how to recover? |

## Evidence labels

Use clear labels instead of blurring documentation and observation:

- **Documented baseline:** repository content and its last reviewed date.
- **User report:** information supplied in the current request.
- **Live observation:** a command, dashboard, or provider result with its timestamp and scope.
- **Unknown:** a question that needs verification.

Avoid credentials, private keys, internal addresses when they are sensitive, provider tokens, and copied command output that may contain them. A record may name the secret manager entry's owner and rotation runbook without naming the secret itself.

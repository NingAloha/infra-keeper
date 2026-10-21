---
name: infrakeeper
description: Safely inspect, document, diagnose, and plan maintenance for a personal infrastructure repository. Use for existing devices, servers, networks, domains, deployed services, or infrastructure changes; do not use for generic application-only work.
metadata:
  short-description: Maintain documented infrastructure safely
---

# InfraKeeper

Use the infrastructure repository as the configuration baseline before answering questions about an existing device or service. Treat repository records as historical documentation, not proof of live state.

## Orient before advising

1. Locate the repository and read its root `README.md` to understand its inventory and conventions.
2. Read the affected device's `README.md` before its focused files (such as `system.md`, `network.md`, `services/`, or `operations.md`). Read only material relevant to the request.
3. For traffic between devices, inspect both endpoints. For public names, DNS, reverse proxies, or ingress, also inspect the domain/routing documentation.
4. State what is documented, what the user has newly reported, and what would need live verification. Prefer the newest evidence when they disagree.

Use [the repository guide](references/repository-guide.md) when locating records or proposing a documentation layout. Use [the maintenance playbook](references/maintenance-playbook.md) for diagnosis, change planning, or an incident.

## Safe maintenance behavior

- Start with read-only discovery. Do not infer credentials, addresses, ports, provider accounts, or runtime health from missing documentation.
- Surface conflicts before recommending a change: overlapping ports, DNS ownership, ingress paths, resource limits, dependencies, and maintenance windows.
- Separate a proposed command or plan from an authorized execution. Do not modify hosts, cloud resources, DNS, or repositories without explicit authorization.
- Prefer incremental, reversible changes. For a change plan, include a pre-change check, success signal, rollback path, and the evidence that will be recorded afterward.
- Never place secrets, private keys, tokens, full credentials, or personally identifying network details in documentation, examples, logs, or responses. Use descriptive placeholders and point to an external secret manager.

## Deliverables

Match the output to the request:

- **Question or inventory request:** concise documented baseline, uncertainty, and relevant next check.
- **Troubleshooting:** evidence, likely hypotheses ranked by impact, safe checks, and a stop/escalation condition.
- **Change proposal:** compatibility findings, staged plan, validation, rollback, and documentation updates.
- **Documentation work:** update the smallest set of records that makes ownership, current state, dependencies, and evidence boundaries clear.

For a starter repository, copy or adapt only the needed files from `templates/infrastructure/`. The fictional repository in `examples/fictional-studio/` illustrates the desired documentation depth; it is not a deployment recipe.

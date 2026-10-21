---
name: infra-keeper
description: Maintain documented infrastructure using GitHub MCP or GitHub CLI, including repository discovery, evidence review, safe change proposals and explicitly approved commits to main.
---

# InfraKeeper

InfraKeeper helps an agent maintain a **versioned infrastructure documentation repository**. This foundation covers GitHub documentation operations, **not** live infrastructure changes.

## Select a GitHub backend

Read [GitHub backends](references/github-backends.md) first.

1. Prefer an available, authenticated **GitHub MCP** connection that provides the required operation.
2. If MCP is not configured or lacks a required capability, use the local **GitHub CLI (`gh`)** only when shell access and a properly authenticated CLI are available **and the switch is permitted and clearly disclosed**.
3. Do not silently change execution backends, and **never switch backends to evade a tool denial, policy prohibition, safety rejection, or access-control restriction**.
4. If neither backend is usable, explain how to configure one; provide a read-only plan rather than pretending access.

Read [MCP instructions](references/github-mcp.md) or [CLI instructions](references/github-cli.md) according to the selected backend. A Skill supplies instructions; it cannot itself provision GitHub access or grant scopes.

## Repository discovery and evidence

1. Use the user's explicit repository selection or the repository established in context. Otherwise discover accessible repositories; ask when ambiguous.
2. Work with `main`; do not create a branch to work around a missing or protected `main`.
3. Read the root inventory and relevant device/service README before specific system, network, operations, or service records.
4. For inter-device requests read both endpoints; for public ingress, DNS, or domain tasks also read the routing documentation.
5. Distinguish **documented baseline**, **user report**, **timestamped live observation supplied by an authorized source**, and **unknown**. Repository text is never proof of present runtime health.

## Single-branch permissions

Follow [GitHub workflow](references/github-workflow.md):

- Read/search/history/status: automatic.
- **Every mutation** (create, edit, append, move, delete, multi-file sync, rollback commit): require explicit approval of the proposed paths, content/diff, and risk.
- No branch management, PR creation/merges, force-push, history rewriting, or repository administration.
- Check current versions before writing, and verify commit and final files afterward.
- Stop on conflicts or tool/policy denials; do not evade restrictions.
- Do not commit secrets or sensitive infrastructure details into public fixtures.

## Scope

No SSH, cloud mutations, server commands, runtime monitoring or DNS changes are provided by this version. GitHub writes change **documentation**, not live services.

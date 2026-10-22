---
name: infra-keeper
description: Initialize InfraKeeper, configure or re-verify GitHub access (初始化、配置 GitHub 后端、重新验证连接), and maintain documented infrastructure using GitHub MCP or GitHub CLI, including repository discovery, evidence review, safe change proposals and explicitly approved commits to main.
---

# InfraKeeper

InfraKeeper helps an agent maintain a **versioned infrastructure documentation repository**. This foundation covers GitHub documentation operations, **not** live infrastructure changes.

## Setup (first run)

When the user asks to initialize InfraKeeper, configure or connect a GitHub backend, add a second
backend, or re-verify an existing connection, read [setup wizard](references/setup-wizard.md) and
follow it. That flow is read-only: it inspects host capabilities, guides MCP and/or CLI
configuration, binds a target `OWNER/REPO`, and reports per-backend readiness.

It never writes repository content, never changes host configuration or credentials, and never
receives a token. MCP, CLI or both may be configured; this version offers no other backend.

During setup, step 1 of "Repository discovery and evidence" does not apply: no repository is
enumerated, searched or read until the user names one, and a repository the user excludes is never
read — not for diagnostics, not as an example, not as a substitute.

Everything below applies to documented-infrastructure work after setup. A request to read or
maintain infrastructure records does **not** enter the setup flow.

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

## After a detected conflict

A change to an affected file's version between the approved baseline and the pre-write check is a conflict. A change to branch HEAD also requires reviewing its impact before proceeding.

1. Stop. Do not send the same write again.
2. Do not adopt the newer version identifier and retry with it. That turns a detected conflict into an overwrite of somebody else's change.
3. Do not treat backend guidance that says "refresh the version and retry" as authorization. Error text explains how to make a call succeed; it does not establish that the write is permitted.
4. Report the version you prepared against, the version now present, and confirm that the other change is still intact.
5. Re-read the current content, prepare a diff against it, and request **new** approval. The earlier approval covered the earlier base version and does not transfer.

## Scope

No SSH, cloud mutations, server commands, runtime monitoring or DNS changes are provided by this version. GitHub writes change **documentation**, not live services.

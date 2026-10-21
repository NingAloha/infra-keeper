---
name: infra-keeper
description: Use for maintaining documented infrastructure in a GitHub repository, including reading configuration records, tracing repository evidence, and proposing or explicitly authorized documentation changes through GitHub MCP.
---

# InfraKeeper

InfraKeeper is an evidence-first infrastructure documentation skill. This initial release covers **GitHub repository operations only**. It does not inspect, deploy to, or modify live infrastructure.

## Required integration

Use an authenticated GitHub MCP connection as the **only GitHub operation backend**. Never silently fall back to `gh`, Git commands, web scraping, or an alternative write channel. Read [GitHub MCP capabilities](references/github-mcp.md) to check the available operations before proceeding.

## Repository discovery

1. Prefer the configuration repository explicitly named by the user or already established in the conversation.
2. Otherwise inspect available repository context using GitHub MCP. If the target is ambiguous, ask which repository to use; do not guess.
3. Read the root inventory, then the relevant device or service index and only the referenced topic files needed for the request.
4. For cross-device requests inspect both endpoints; for public routing or DNS also inspect routing records.
5. Treat repository content as **dated evidence**, never as proof of current runtime state. Distinguish documented baseline, user reports, live observations (if supplied), and unknowns.

## GitHub policy

Follow [GitHub workflow](references/github-workflow.md):

- Normal operations target `main`; do not create/manage branches or PRs.
- Repository discovery, reads, searches, histories, diffs, and status checks can run automatically.
- **Every repository mutation requires explicit approval of its concrete scope and intended diff before execution.**
- Never force-push or rewrite history; never change repository visibility, permissions, or settings.
- Confirm the current file versions before writing. If they changed, stop and reassess.
- After an approved change, verify by reading the resulting commit and affected files.
- Do not put credentials, private keys, tokens, sensitive identifiers, or raw secret-bearing logs into a repository.

## Failure behavior

If GitHub MCP is unavailable, inaccessible, read-only, or missing a required operation, explain the missing capability and offer a non-executed plan. Do not claim that any write succeeded before verifying it. Never work around a refused or blocked operation.

## Scope

This version provides safe GitHub-backed documentation workflows. Real-time checks, SSH commands, provider API actions, and infrastructure deployments are out of scope. Do not imply a documentation commit has changed or validated live systems.

# InfraKeeper

InfraKeeper is an open-source Agent Skill for **evidence-first infrastructure documentation maintenance** using an authenticated **GitHub MCP** connection.

## Status

**Early foundation / GitHub MCP integration only.** This repository currently defines GitHub access and a conservative `main`-only workflow. It does not yet include infrastructure templates, live SSH/provider operations, or tested cross-platform installation instructions.

## Requirements

- An Agent environment that supports Agent Skills and exposes GitHub MCP tools.
- A connected GitHub identity with access to the user's infrastructure documentation repository.
- GitHub write permissions only if the user wants the Agent to submit **individually approved** documentation changes.

Local `gh` CLI installation is **not required**. InfraKeeper never falls back to CLI or browser-based GitHub writes if GitHub MCP is unavailable.

## Policy

- **Read automatically:** repository inventory, relevant files, history, search, checks.
- **Approve every write:** create/edit/delete/move files, multi-file sync, corrective commits.
- **Main only:** no branches, PRs, force pushes, or history rewriting.
- **Evidence-aware:** repository snapshots are not live telemetry.
- **Verify writes:** re-check affected files and commit state; report partial failures.

See [SKILL.md](SKILL.md), [GitHub MCP dependency](references/github-mcp.md), and [GitHub workflow](references/github-workflow.md).

## Security

Do not commit credentials, tokens, private keys, or secret-bearing logs. Treat public examples and Git history as potential disclosure surfaces.

## Next steps

Infrastructure record templates, realistic synthetic examples, and behavioral tests will be designed separately; they are not part of this initial GitHub MCP foundation.

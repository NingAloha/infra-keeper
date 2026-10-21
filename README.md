# InfraKeeper

InfraKeeper is an experimental, portable **Agent Plugin** wrapping a standard **Agent Skill** for evidence-first infrastructure documentation maintenance.

## Package layout

```text
plugin.json
skills/infra-keeper/SKILL.md
skills/infra-keeper/references/
  github-backends.md
  github-mcp.md
  github-cli.md
  github-workflow.md
```

The root `plugin.json` follows [Agent Plugins v1](https://agent-plugins.org/specification). The embedded Skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Install / requirements

Use an Agent environment supporting Agent Plugins v1 to install this repository as a plugin. Clients that support standalone Skills can use `skills/infra-keeper/` directly. **Installation is not authentication**: configure either an authorized GitHub MCP connection (preferred) or an installed/authenticated GitHub CLI (`gh`) with shell execution.

This version does **not** bundle an MCP server or automatically provision GitHub credentials. It has not yet been validated with Hermes Desktop or ChatGPT/Codex, and plugin support varies by client.

## Safety and operation

- Work against `main`; do not create/manage branches or PRs.
- Automatic reads; explicit, diff-specific authorization for **every repository mutation**.
- Never force-push, rewrite history, change repository settings, or bypass a denied operation by switching backends.
- Check concurrent edits before writing; read back the commit and affected paths afterward.
- Repository documentation is dated evidence, not live service status.
- Never publish tokens, secrets, private keys, or sensitive infrastructure identifiers.

## Scope

This foundation only supplies GitHub-backed documentation workflows. Infrastructure templates, actual deployment tools, and end-to-end Agent tests are future work.

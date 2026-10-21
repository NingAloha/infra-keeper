# InfraKeeper

InfraKeeper is an experimental **Agent Plugin** that packages a standard **Agent Skill** for evidence-first infrastructure documentation maintenance.

## Package layout

```text
plugin.json
skills/infra-keeper/SKILL.md
skills/infra-keeper/references/
  github-backends.md
  github-mcp.md
  github-cli.md
  github-workflow.md
docs/hermes.md
tests/
  hermes-smoke-test.md
  hermes-mcp-smoke-test.md
  integration/mcp-lifecycle.md
```

The plugin packaging is intended for [Agent Plugins](https://agent-plugins.org/specification); the embedded Skill uses the [Agent Skills specification](https://agentskills.io/specification). Compatibility must be verified separately per host.

## Installation and GitHub access

Install this repository in a compatible Agent Plugin host, or load `skills/infra-keeper/` directly in an Agent Skills host. **Installing a Skill or Plugin does not authenticate GitHub or install its tool dependencies.**

Choose one authorized backend:
- **GitHub MCP (preferred):** Connect a compatible GitHub MCP server to the Agent host. Official implementation: https://github.com/github/github-mcp-server
- **GitHub CLI (`gh`):** For local Agents with shell access, install and authenticate https://cli.github.com/ and verify with `gh auth status`.

See [Hermes Desktop integration notes](docs/hermes.md) for the tested setup and limitations.

## Safety policy

- Normal documentation changes go directly to `main`; do not manage branches or PRs.
- Reads, searches, history and status checks may be automatic.
- **Every write** requires specific prior approval of the proposed path(s), content/diff, impact and rollback.
- Check for concurrent edits before writing; re-read the commit and changed files afterward.
- Do not force-push, rewrite history, change repository administration, or switch backends to bypass a denial.
- Repository documentation is **historical evidence**, not proof of current service health.
- Never commit credentials, private keys, tokens, or sensitive infrastructure details to public examples.

## Verification status (2026-10-22)

Hermes Desktop has successfully **loaded the plugin and Skill** and completed authenticated read, approval-before-write, and read-back checks through **both** GitHub CLI and GitHub MCP. The MCP backend has additionally completed a five-stage lifecycle test on `main`.

| Backend | Evidence | Confirmed | Not yet tested |
| --- | --- | --- | --- |
| GitHub CLI | [CLI smoke test](tests/hermes-smoke-test.md) | Read, approval, create file, commit and read-back | Existing-file update, delete/rollback, conflict handling. **No advanced lifecycle test has been run on this backend** |
| GitHub MCP | [MCP smoke test](tests/hermes-mcp-smoke-test.md), [MCP lifecycle test](tests/integration/mcp-lifecycle.md) | Tool discovery, read, approval, create, update guarded by blob SHA, stop on a concurrent edit, delete, restore by a new commit, read-back | GitHub-side version enforcement (see note), multi-file atomic commit, move/rename, permission-denied behavior |

**Scope note on the conflict evidence:** the stale-version write was rejected on the **MCP write path**. The returned message does not establish whether the comparison happened in the MCP server or in the GitHub API, so this repository does **not** claim that GitHub itself enforced version checking.

These were manual, single-environment acceptance tests, **not automated conformance tests**. The CLI and MCP smoke-test evidence was committed as [CLI test `09f4ad2`](https://github.com/NingAloha/infra-keeper/commit/09f4ad22076856123d2cc99674b36b32812a62cd) and [MCP test `fb31c65`](https://github.com/NingAloha/infra-keeper/commit/fb31c65c3392c99a3e39007b39911f4b9fa3eb40); the lifecycle stages are commits [`6f336ade`](https://github.com/NingAloha/infra-keeper/commit/6f336adeb15de0892b4fba2bf6a2367810f3ffd5), [`f87b3313`](https://github.com/NingAloha/infra-keeper/commit/f87b33138937139a96843efcef928c32bceae4c6), [`73fe73b8`](https://github.com/NingAloha/infra-keeper/commit/73fe73b8ce9329a19c4e5527e693fc8db36299ac), [`b95e8bee`](https://github.com/NingAloha/infra-keeper/commit/b95e8beebb738e6e33b9eb102b684ad1d07c1712) and [`3be2869d`](https://github.com/NingAloha/infra-keeper/commit/3be2869d01527efb891213543003aec0c157e521). ChatGPT/Codex plugin installation has not been separately validated.

## Current scope

Only **GitHub-backed documentation workflows** are implemented. Infrastructure inventory templates, live SSH/cloud operations, reproducible test automation, and full multi-platform validation are future work. Conflict handling has been exercised once, manually, on the MCP backend only; it is neither automated nor tested on the CLI backend.

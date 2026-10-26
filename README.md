# InfraKeeper

**English** | [简体中文](README.zh-CN.md)

InfraKeeper is an experimental **Agent Plugin** that packages a standard **Agent Skill** for evidence-first infrastructure documentation maintenance.

## Quick start

1. Install this repository in a compatible Agent Plugin host (see below).
2. Say **“初始化 InfraKeeper”** or **“Set up InfraKeeper”**. The Skill opens its read-only setup wizard.
3. Use the local **GitHub CLI (`gh`)**. This version no longer uses GitHub MCP; the bundled CLI helper
   calls the user's authenticated `gh` and never receives or stores a token.
4. Tell the wizard which repository to use (`OWNER/REPO`). It reports one CLI verdict:
   `ready`, `unavailable`, `unauthenticated`, `insufficient-permissions` or `unverified`.

The wizard is **read-only**. It never creates a test commit or test file, and it never changes host
configuration, environment variables or credential files by itself. You complete `gh auth login`
and credential setup yourself; the Skill never asks for, displays or stores a token.

Setup ends by pointing at a device audit. That audit is **not implemented** in this version.

## Package layout

```text
README.md
README.zh-CN.md
plugin.json
skills/infra-keeper/scripts/gh_backend.py
skills/infra-keeper/SKILL.md
skills/infra-keeper/references/
  github-backends.md
  github-cli.md
  github-workflow.md
  setup-wizard.md
docs/hermes.md
tests/
  test_gh_backend.py
  hermes-smoke-test.md
  integration/cli-lifecycle.md
```

The plugin packaging is intended for [Agent Plugins](https://agent-plugins.org/specification); the embedded Skill uses the [Agent Skills specification](https://agentskills.io/specification). Compatibility must be verified separately per host.

## Installation and GitHub access

Install this repository in a compatible Agent Plugin host, or load `skills/infra-keeper/` directly in an Agent Skills host. **Installing a Skill or Plugin does not authenticate GitHub or install `gh`.** Install and authenticate GitHub CLI in your own terminal, then verify with `gh auth status`.

Choose one authorized backend:
- **GitHub CLI (`gh`):** For local Agents with shell access, install and authenticate https://cli.github.com/ and verify with `gh auth status`.

The bundled `skills/infra-keeper/scripts/gh_backend.py` wraps common GitHub operations as structured
JSON and requires approval plus SHA preconditions for writes.

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

Hermes Desktop has successfully **loaded the plugin and Skill** and completed authenticated read, approval-before-write, and read-back checks through **GitHub CLI**. The CLI path has additionally completed a five-stage lifecycle test on `main`.

| Backend | Evidence | Confirmed | Not yet tested |
| --- | --- | --- | --- |
| GitHub CLI | [CLI smoke test](tests/hermes-smoke-test.md), [CLI lifecycle test](tests/integration/cli-lifecycle.md) | Read, approval, create, update guarded by blob SHA, stop on a concurrent edit, server-side rejection of a stale SHA (`409`), delete conditioned on the blob SHA, byte-exact restore, read-back | Stale-`sha` **delete** rejection (only the matching case was run), multi-file atomic commit, move/rename, permission-denied behavior, two independent accounts |
| Bundled CLI helper | [Unit tests](tests/test_gh_backend.py) | JSON CLI validation, approval gate, stale blob SHA rejection | Live GitHub end-to-end run, cross-host installation |

**Setup wizard status:** the wizard protocol is documented and committed, but it has not yet been
exercised in an acceptance run. This table reports CLI and helper verification, not wizard behaviour.

**Scope note on the conflict evidence:** GitHub CLI is the only active backend. The stale-SHA write was rejected with an HTTP `409` response carrying `Server: github.com` and a GitHub request ID, so for the REST Contents API this repository claims server-side enforcement of the `sha` precondition.

These were manual, single-environment acceptance tests, **not automated conformance tests**. The CLI smoke-test evidence was committed as [CLI test `09f4ad2`](https://github.com/NingAloha/infra-keeper/commit/09f4ad22076856123d2cc99674b36b32812a62cd); the CLI lifecycle stages are commits [`5d350208`](https://github.com/NingAloha/infra-keeper/commit/5d350208272823d861b42b93b6d79ad4b3cd538b), [`05a7c7f8`](https://github.com/NingAloha/infra-keeper/commit/05a7c7f8c7d84d82890b29f047f035a781808b0e), [`ed63fad4`](https://github.com/NingAloha/infra-keeper/commit/ed63fad49e650bccd1ef96d8c0ca2989924b2d6e) (web editor), [`95b3d34b`](https://github.com/NingAloha/infra-keeper/commit/95b3d34b9ecde11fac08256c06b8504b5f3ba295) and [`343b25fa`](https://github.com/NingAloha/infra-keeper/commit/343b25faf305dbc9514da12330c73965171156ce); the C-2 rejection produced no commit. ChatGPT/Codex plugin installation has not been separately validated.

## Current scope

Only **GitHub-backed documentation workflows** are implemented. Infrastructure inventory templates, live SSH/cloud operations, and full multi-platform validation are future work. **A device audit does not exist yet** — setup only prepares access to the repository that such an audit would read. Conflict handling is exercised through GitHub CLI and covered by unit tests for the bundled helper's approval and version checks. No GitHub MCP, Local Workspace or Local Git backend exists in this version.

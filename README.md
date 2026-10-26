# InfraKeeper

**English** | [简体中文](README.zh-CN.md)

InfraKeeper is an experimental **Agent Plugin** that packages a standard **Agent Skill** for evidence-first infrastructure documentation maintenance.

## Quick start

1. Install this repository in a compatible Agent Plugin host (see below).
2. After installation, start any relevant InfraKeeper task. The Agent automatically runs a read-only
   preflight; with no binding on the first run it opens the bootstrap flow, then only verifies the
   binding on later runs.
3. The preflight first detects the local **GitHub CLI (`gh`)** in the Agent page. If it is missing, it
   shows an official installation command and its effect; after approval, the Agent page runs it and
   re-checks.
4. If the CLI is not authenticated, the setup flow shows `gh auth login` and requests separate approval
   before starting it in the Agent page. The user completes browser authorization. If the host cannot
   provide an interactive terminal, the wizard falls back to the user's terminal. It never receives,
   displays or stores a token.
5. If no local binding exists, choose a repository name; the default is `infrastructure`. If it already exists,
   the wizard asks for an unused name, requests one separate approval, creates a private personal
   repository, and verifies it. Later runs only verify the stored binding. It reports one CLI verdict:
   `ready`, `changed-since-state`, `unavailable`, `unauthenticated`, `insufficient-permissions`,
   `out-of-scope` or `unverified`.

This version operates only on repositories **owned by the authenticated GitHub user**. Organization,
collaborator and other-user public repositories are rejected even when the account can access them.

After first-run bootstrap, the wizard is **read-only for GitHub**. The first run may create exactly
one private personal repository with an initial README after separate approval; it never creates a
test commit or silently installs packages. Every installation, login or repository-creation command
is shown with its effect and requires separate approval, preferably in the Agent page. It falls back
to the user's terminal only when the host lacks the required capability, and never asks for, displays
or stores a token.

After S5 succeeds, InfraKeeper stores only binding metadata in a local app state file: the repository,
`main` branch, the last confirmed GitHub `main` HEAD SHA, bootstrap status and optional initial commit
SHA. After every successful documentation commit, that checkpoint is updated from GitHub's returned
commit SHA. On multiple devices, a new agent session advances its local checkpoint automatically when
GitHub's `main` is a normal descendant of it and then continues the ready flow. If the remote branch
has been rewound, diverged or rewritten, the change is reported and automatic writes stop. It never
stores tokens, `gh` credentials or repository contents.

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
```

The plugin packaging is intended for [Agent Plugins](https://agent-plugins.org/specification); the embedded Skill uses the [Agent Skills specification](https://agentskills.io/specification). Compatibility must be verified separately per host.

## Installation and GitHub access

Install this repository in a compatible Agent Plugin host, or load `skills/infra-keeper/` directly in an Agent Skills host. Installing the plugin does not silently install or authenticate GitHub CLI. On the first relevant task, the Agent automatically runs the setup preflight; it detects `gh`, gives OS-specific official installation guidance when needed, and can run an exact installation or login command in the Agent page only after separate approval.

Choose one authorized backend:
- **GitHub CLI (`gh`):** For local Agents with shell access, install and authenticate https://cli.github.com/ and verify with `gh auth status`.

The bundled `skills/infra-keeper/scripts/gh_backend.py` wraps common GitHub operations as structured
JSON and requires approval plus SHA preconditions for writes.

See [Hermes Desktop integration notes](docs/hermes.md) for setup guidance.

## Safety policy

- Normal documentation changes go directly to `main`; do not manage branches or PRs.
- The target repository owner must match the authenticated `gh` user; organization, collaborator and other-user repositories are out of scope.
- On the first run with no binding, create one private personal repository only after separate approval; later setup runs never create another repository.
- Reads, searches, history and status checks may be automatic.
- **Every write** requires specific prior approval of the proposed path(s), content/diff, impact and rollback.
- Check for concurrent edits before writing; re-read the commit and changed files afterward.
- Do not force-push, rewrite history, change repository administration, or switch backends to bypass a denial.
- Repository documentation is **historical evidence**, not proof of current service health.
- Never commit credentials, private keys, tokens, or sensitive infrastructure details to public examples.

## Current scope

InfraKeeper maintains versioned infrastructure documentation in personal GitHub repositories through
the local GitHub CLI. It supports evidence-first workstation and server records, guarded documentation
writes on `main`, local binding state and automatic setup preflight.

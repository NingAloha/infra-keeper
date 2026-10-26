# Hermes Desktop integration notes

These notes describe an actual **macOS Hermes Desktop test on 2026-10-22**. They are
environment-specific observations, not guarantees about every Hermes version.

## Plugin installation

Install this GitHub repository using Hermes Desktop's **Plugin** installer:

```text
https://github.com/NingAloha/infra-keeper
```

Hermes recognized the root `plugin.json` and loaded the embedded
`skills/infra-keeper/SKILL.md`. An earlier root-only `SKILL.md` layout was not recognized by that
plugin installer.

## GitHub CLI path

On the tested Mac, `gh` v2.101.0 was already authenticated. Hermes used its local shell capability
to read repository records and, after explicit approval, create and verify a documentation commit.
The setup wizard now detects whether `gh` is present and gives one-step-at-a-time installation
guidance when it is missing. Hermes should run the exact command in the Agent page after explicit
approval; use the user's terminal only if Hermes cannot provide the required command or interactive
terminal capability. Never paste a token into a prompt.

The bundled helper at `skills/infra-keeper/scripts/gh_backend.py` calls `gh api` without a shell and
prints structured JSON. It keeps authentication in the user's existing `gh` credential mechanism,
requires `--approved` for writes, and checks blob SHA / branch HEAD preconditions before using the
GitHub Contents API.

Use `gh --version` and `gh auth status` to check local readiness. The local checkout of this plugin
was read for reference only and was never used as a write path during the lifecycle run; writes were
performed through the GitHub API exposed by `gh`.

## Setup wizard on this installation

Before the first relevant InfraKeeper task in a new Hermes session, the agent automatically runs the
setup preflight; the user does not need to say **「初始化 InfraKeeper」** first. Explicit requests such
as **「初始化 InfraKeeper」** or **"Set up InfraKeeper"** also route to the same flow instead of the
documentation workflow.

The wizard checks local command capability and `gh` authentication. If `gh` is missing, it asks for
the operating system, shows the exact official installation command and its effect, and requests
separate approval before running it. It then re-runs `gh --version`. If authentication is missing,
it similarly shows `gh auth login` and requests a separate approval before starting it in the Agent
page; the user completes the browser/device authorization. If Hermes cannot keep that command
interactive, provide a terminal fallback. It does not inspect or configure credential files, shell
profiles or repository content before the local state identifies a binding or the user names a repository.

After the user names a repository, Hermes verifies that its owner matches the authenticated GitHub
login. Organization, collaborator and other-user repositories are rejected before repository reads.

On the first setup run with no stored binding, Hermes asks for a repository name, defaults to
`infrastructure`, checks that the name is unused under the authenticated user, and requests one
separate approval before creating a private repository with an initial README. After the repository
is verified and bound, later setup runs only re-check it and never create another repository.

After a successful verification, the bundled helper writes a small local state file containing only the
binding metadata, `main` branch, bootstrap status and optional initial commit SHA. A new Hermes session
reads that file before repository work or asking for a name, then still re-verifies the recorded repository through `gh`.
The file contains no token, credential data or repository contents. If Hermes cannot read or persist the
file, the current run can still finish, but the next session may ask for the repository again.

## Limitations

- This source package does not ship test fixtures, acceptance logs or automated conformance tests.
- Readiness checks do not establish write permission until the target repository is read and the intended operation is authorized.
- Multi-file commits, move/rename, and permission-denied behavior require separate validation.
- No actual cloud server, DNS or device is contacted by the plugin.

## Reload after an update

After changing the Skill or helper, reload the plugin. Starting a new Hermes session is advised if
the Skill description or references still look stale.

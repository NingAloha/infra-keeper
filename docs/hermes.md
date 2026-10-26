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
The Skill does not install `gh` or authenticate it. Never paste a token into a prompt.

The bundled helper at `skills/infra-keeper/scripts/gh_backend.py` calls `gh api` without a shell and
prints structured JSON. It keeps authentication in the user's existing `gh` credential mechanism,
requires `--approved` for writes, and checks blob SHA / branch HEAD preconditions before using the
GitHub Contents API.

Use `gh --version` and `gh auth status` to check local readiness. The local checkout of this plugin
was read for reference only and was never used as a write path during the lifecycle run; writes were
performed through the GitHub API exposed by `gh`.

## Setup wizard on this installation

The setup wizard is entered in natural language. After installing or updating the plugin, a request
such as **「初始化 InfraKeeper」** or **"Set up InfraKeeper"** routes to the setup wizard instead of
the documentation workflow.

The wizard now checks only local command capability and `gh` authentication. It does not inspect or
configure credential files, shell profiles or repository content before the user names a repository.

## Evidence and limitations

- [CLI execution evidence](../tests/hermes-smoke-test.md): approval-before-write and single-file creation on `main`.
- [CLI lifecycle evidence](../tests/integration/cli-lifecycle.md): the lifecycle run through `gh api`, including a server-side rejection of a stale blob SHA.
- [CLI helper unit tests](../tests/test_gh_backend.py): parameter validation, approval gate and stale-SHA preflight.
- Readiness checks do not establish write permission until the target repository is read and the intended operation is authorized.
- Multi-file commits, move/rename, and permission-denied behavior are not yet exercised by the helper.
- No actual cloud server, DNS, or device was contacted by these tests.

## Reload after an update

After changing the Skill or helper, reload the plugin. Starting a new Hermes session is advised if
the Skill description or references still look stale.

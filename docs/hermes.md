# Hermes Desktop integration notes

These notes describe an actual **macOS Hermes Desktop test on 2026-10-22**. They are environment-specific observations, not guarantees about every Hermes version.

## Plugin installation

Install this GitHub repository using Hermes Desktop's **Plugin** installer:

```text
https://github.com/NingAloha/infra-keeper
```

Hermes recognized the root `plugin.json` and loaded the embedded `skills/infra-keeper/SKILL.md`. An earlier root-only `SKILL.md` layout was **not** recognized by that plugin installer.

## GitHub CLI path

On the tested Mac, `gh` v2.101.0 was already authenticated. Hermes used its local shell capabilities to read repository records, then — after explicit approval — created `tests/hermes-smoke-test.md` and verified the resulting commit.

Use `gh --version` and `gh auth status` to check local readiness. The Skill does not install `gh` or authenticate it. Never paste a token into a prompt.

A later lifecycle run on this path used `gh api` against the REST Contents API for every write, so all commits were created by the API rather than by a local Git client. The local checkout of this plugin was read for reference only and was never used as a write path.

## GitHub MCP path

The tested Hermes installation connected to GitHub's hosted MCP endpoint:

```text
https://api.githubcopilot.com/mcp/
```

An initial OAuth auto-registration attempt failed because the provider did not expose a dynamic client registration endpoint. A **repository-scoped fine-grained PAT** supplied through an environment-variable-backed Bearer header worked in this installation.

Illustrative configuration excerpt (verify field names against your Hermes version):

```yaml
mcp_servers:
  github:
    url: "https://api.githubcopilot.com/mcp/"
    headers:
      Authorization: "Bearer ${GITHUB_MCP_TOKEN}"
    enabled: true
```

The secret must be stored outside the Git repository, using Hermes-supported private environment/credential storage, with restrictive permissions. Do not copy the literal token into this YAML, logs, chat, or a public example. Restrict the PAT to the repositories and permissions needed; start read-only and grant Contents write only when testing authorized commits.

The `hermes mcp test github` command connected and discovered tools. After changing MCP configuration, an existing Hermes chat session did not initially expose the tools, despite a successful Gateway registration log. Opening a **new session** resolved the issue in this test.

## Setup wizard on this installation

The setup wizard is entered in natural language. After installing or updating the plugin, a request
such as **「初始化 InfraKeeper」** or **"Set up InfraKeeper"** routes to the
[setup wizard](../skills/infra-keeper/references/setup-wizard.md) instead of the documentation
workflow.

What this host can and cannot observe:

| Signal | Observable here | What it does not prove |
| --- | --- | --- |
| GitHub MCP tools exposed to the session | yes — they appear in the session's tool list | that the MCP server holds a valid identity, or that the identity can read a given repository |
| Local shell and `gh` | yes — `gh --version` and `gh auth status` | repository permission; scopes printed by `gh auth status` are not a repository verdict |
| Host credential stores, token contents, MCP server internals | no | anything about their state |

Tool presence is not authentication, and authentication is not repository access. The wizard
therefore reports one verdict per backend and per repository — `ready`, `unavailable`,
`unauthenticated`, `insufficient-permissions` or `unverified` — rather than a single global
"connected" state.

MCP, CLI, or both may be configured, and each path reports its own read-only readiness. One working
backend is enough to continue; the second can be added later.

**Reload after an update.** For MCP configuration changes this installation *verified* that an
existing chat session did not expose the newly configured tools until a new session was opened (see
"GitHub MCP path" above). For plugin updates that change only Skill text, reloading the plugin is the
expected step, and starting a new session is **advised** if the Skill description or references still
look stale — that case has not been measured, so treat it as a recommendation rather than a result.

**Wizard status.** The protocol is committed, but this installation has not run it as an end-to-end
interactive acceptance test. Do not describe the wizard as fully working: the measured evidence in
this document covers backend access over the CLI and MCP paths, not wizard behaviour.

## Evidence and limitations

- [CLI execution evidence](../tests/hermes-smoke-test.md): approval-before-write and single-file creation on `main`.
- [MCP execution evidence](../tests/hermes-mcp-smoke-test.md): MCP-only file/history reads, approval-before-write, creation on `main`, and content verification.
- [MCP lifecycle evidence](../tests/integration/mcp-lifecycle.md): five-stage create / guarded update / stop-on-change / stale-version rejection / delete / restore test on `main`, MCP only.
- [CLI lifecycle evidence](../tests/integration/cli-lifecycle.md): the same lifecycle run on `main` entirely through `gh api`, including a server-side rejection of a stale blob SHA.
- Read/write tool discovery by itself does **not** establish access permission.
- The [setup wizard](../skills/infra-keeper/references/setup-wizard.md) has no interactive acceptance run yet; its protocol is documented and committed, but untested end to end.
- Multi-file commits, move/rename, and permission-denied behavior are **not** yet exercised on either backend. A stale-`sha` **delete** rejection is untested on both backends; only the matching case was run.
- No actual cloud server, DNS, or device was contacted by any of these tests.

## MCP lifecycle test (A–E)

Five separately approved stages against `tests/integration/mcp-lifecycle.md`, run entirely through GitHub MCP.

| Stage | Action | Outcome |
| --- | --- | --- |
| A | Create the fixture | One commit, one file, body byte-identical to the approved draft |
| B | Update using the blob SHA read immediately before | Accepted; 13 added, 1 removed, body byte-identical |
| C-1 | Operator edited the same path in the GitHub web editor between approval and write | Agent re-read, saw a different blob SHA, made **zero** write calls, reported both SHAs |
| C-2 | The same stale SHA resubmitted as a deliberate negative test | Rejected; no commit; `HEAD` and file unchanged |
| D | Delete the fixture | One commit, exactly one path removed |
| E | Restore the pre-delete copy by a new commit | Blob SHA returned to its pre-delete value; commit SHA new |

Verified on this backend: create; update guarded by a version identifier; stopping on a detected concurrent change; rejection of a stale version identifier; delete; and content-exact restore without rewriting history.

Not verified: whether the rejection came from the GitHub API or from the MCP server before the request left the client; multi-file or atomic commits; move/rename; permission-denied behavior; conditional delete; two independent human accounts acting concurrently.

On the MCP backend, the server's `delete_file` accepts only `owner`, `repo`, `path`, `message` and `branch`. It takes no version identifier, so a delete cannot be conditioned on the version the agent read. Re-reading immediately before deleting, and checking the resulting commit's file list, are detection measures only — they do not make the delete conditional. A concurrent edit inside that window can therefore remove the latest file state without a fresh approval, although earlier versions remain in the commit history and can be restored by a new commit.

## CLI lifecycle test (A–E)

The same six stages were then run against `tests/integration/cli-lifecycle.md`, entirely through
`gh api` (GitHub CLI 2.101.0, REST Contents API). No MCP tool was used, no local Git client wrote,
and no branch or pull request was created.

| Stage | Action | Outcome |
| --- | --- | --- |
| A | Create the fixture without `sha` | `201`; one commit, `+63/-0`, body byte-identical to the approved draft |
| B | Update with the blob SHA read immediately before | one commit, `+17/-1`; new blob matched the value computed in advance |
| C-1 | Operator edited the same path in the web editor after approval | Agent re-read, saw a different blob SHA and a different `HEAD`, made **zero** write calls, and discarded the approved draft |
| C-2 | The stale SHA resubmitted with content byte-identical to the current file | `409 Conflict` from the GitHub API; no commit; `HEAD`, blob and bytes unchanged |
| D | Delete with the current blob SHA as a precondition | `200`; one commit, `-82`, path removed |
| E | Restore the pre-delete copy by a new commit, without `sha` | `201`; one commit, `+82`; blob and tree identical to the pre-delete state, commit SHA new |

Verified on this backend: the `sha` precondition on `PUT` is enforced by the server that creates
the commit (a matching value is accepted, a stale one is rejected with `409` and no side effects);
a concurrent edit inside the approval window is caught by the client-side guard; a `DELETE`
carrying a matching `sha` succeeds; and content can be restored byte for byte by a new commit.

Not verified: whether a **stale** `sha` is also rejected on `DELETE` (only the matching case was
run, because a failed assertion there would have removed a path); multi-file or atomic commits;
move/rename; permission-denied behavior; two independent human accounts acting concurrently.

The two backends are not interchangeable evidence. On this CLI path the `409` carried
`Server: github.com`, `X-Github-Request-Id` and `X-Github-Api-Version-Selected`, which locates the
rejection at the GitHub API. The MCP path produced a prose rejection whose layer — MCP server or
API — remains unidentified.

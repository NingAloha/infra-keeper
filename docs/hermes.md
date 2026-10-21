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

## Evidence and limitations

- [CLI execution evidence](../tests/hermes-smoke-test.md): approval-before-write and single-file creation on `main`.
- [MCP execution evidence](../tests/hermes-mcp-smoke-test.md): MCP-only file/history reads, approval-before-write, creation on `main`, and content verification.
- [MCP lifecycle evidence](../tests/integration/mcp-lifecycle.md): five-stage create / guarded update / stop-on-change / stale-version rejection / delete / restore test on `main`, MCP only.
- Read/write tool discovery by itself does **not** establish access permission.
- Multi-file commits, move/rename, and permission-denied behavior are **not** yet exercised on either backend. The CLI backend has had no advanced lifecycle test.
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

The MCP server's `delete_file` accepts only `owner`, `repo`, `path`, `message` and `branch`. It takes no version identifier, so a delete cannot be conditioned on the version the agent read. Re-reading immediately before deleting, and checking the resulting commit's file list, are detection measures only — they do not make the delete conditional. A concurrent edit inside that window can therefore remove the latest file state without a fresh approval, although earlier versions remain in the commit history and can be restored by a new commit.

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
- Read/write tool discovery by itself does **not** establish access permission.
- Existing-file update with blob SHA, deletion, multi-file commit, forced conflicts, and permission-denied behavior are **not** yet exercised.
- No actual cloud server, DNS, or device was contacted by either smoke test.

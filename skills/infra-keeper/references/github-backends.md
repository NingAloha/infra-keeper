# GitHub backend selection

InfraKeeper supports **two alternative GitHub operation backends**, not two simultaneous mandatory dependencies:

| Backend | Requirements | Best for |
| --- | --- | --- |
| GitHub MCP | MCP-enabled agent host, connected identity, exposed repository tools | Hosted / desktop agent integrations |
| GitHub CLI `gh` | Shell execution, installed `gh`, authenticated account | Local agents, terminals |

## Capability negotiation

1. Resolve repository `OWNER/REPO` from user context, never guess an unrelated repository.
2. Detect available GitHub MCP tools and check whether they can fulfill the specific operation.
3. Otherwise, when local commands are permitted, check `gh --version` and `gh auth status` (never print tokens).
4. State the selected backend and scope before operations. If changing backend during a workflow, disclose the reason.
5. Backend choice **does not** supersede approval, account permissions, platform rules, branch restrictions, or GitHub protections.

A missing tool or unconfigured integration can justify switching to the other supported backend. A **denied operation** cannot: stop instead of trying a second channel to bypass it. Do not combine writes from two backends in one approval scope without renewed review.

## Common behavioral contract

- `main` only; no branch/PR lifecycle or force-push.
- Automatically read/search/history/status.
- Require concrete, explicit authorization before **every write**.
- Refresh file/version information immediately before an approved write; stop if changed.
- Prefer atomic multi-file updates; otherwise disclose and monitor partial success.
- Verify final GitHub state after committing and report commit SHA.
- Public repositories and Git histories must not receive credentials or sensitive internal configuration.
- Documentation verification is not runtime verification.

See [GitHub MCP](github-mcp.md), [GitHub CLI](github-cli.md) and [GitHub workflow](github-workflow.md).

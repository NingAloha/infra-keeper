# GitHub MCP integration

## Dependency contract

GitHub MCP is the **preferred but optional** backend, authenticated by the **host Agent platform**. Users choosing GitHub MCP do not need a locally installed `gh` CLI or an interactive `gh auth login` session. For agents without GitHub MCP, the alternative GitHub CLI backend is described in [github-cli.md](github-cli.md). Actual GitHub repository access and write privileges depend on the connected identity, repository permissions, exposed MCP tools, and platform safety rules.

The skill depends on **capabilities**, not provider-specific MCP function names. On invocation inspect which tools are available.

### Required for read-only functionality

- Discover or inspect an accessible repository.
- Fetch a file by path and (where available) revision.
- Read the repository's default branch or requested revision.

### Needed for richer investigations

- Search files, paths, and repository content.
- Inspect commit history, file history, comparisons, or diffs.
- Inspect commit/status checks.

When a richer read operation is missing, state the limitation and use other authorized **GitHub MCP read operations** if adequate; never invent missing evidence.

### Needed for approved documentation changes

- Create and update files, with current version or blob SHA checks when supported.
- Delete or move files (a move may require coordinated delete/create).
- Commit to `main`, including multi-file updates when supported.
- Read back the commit and affected paths for verification.

If no atomic multi-file commit operation is exposed, disclose the possibility of partial completion before approval and track each completed write. Never claim all-or-nothing semantics where none exist.

## Connection and permission failures

- **No GitHub MCP:** use the GitHub CLI alternative only when installed, authorized and available, per [backend selection](github-backends.md). Otherwise explain the missing connection.
- **Repository inaccessible:** request an authorized connection or correct repository selector. Do not probe unrelated accounts.
- **Read-only integration:** perform only reads, prepare a diff if useful, and explain why no commit can be made.
- **Missing tool:** report the unavailable action; a permitted, disclosed CLI backend may be used for capability gaps, but never to evade a policy or security denial.
- **Tool or safety rejection:** stop; never switch to CLI or another tool to bypass a denied action.
- **Concurrent edit:** fetch newest version, show conflicts, and obtain new approval if changes require a materially revised diff.

## Data handling

Only request access necessary for the target repository. Never ask the user to paste access tokens or keys into repository documents. Redact sensitive values before proposing diffs or reporting command output. A public repository may expose historical content too; avoid copying real infrastructure records as public sample fixtures.

## Verification boundaries

Reading the final repository file confirms **documentation state**, not actual device state. A GitHub MCP response does not establish current service availability, cloud status, DNS propagation, or live configuration.

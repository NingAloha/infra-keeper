# GitHub MCP smoke test — Hermes Desktop

**Date:** 2026-10-22 (CST)
**Repository:** `NingAloha/infra-keeper`
**Branch:** `main` (existing branch; this commit is applied directly to it — no new branch is created)
**Pre-test HEAD:** `09f4ad22076856123d2cc99674b36b32812a62cd` (state observed before this record was created; not the HEAD of the commit that adds this file)
**Backend:** GitHub MCP, authenticated by the Hermes Desktop host platform. Credentials are not recorded here.
**Scope:** repository documentation only. No live infrastructure was contacted, inspected, or modified.

## Purpose

Confirm that the InfraKeeper Skill's GitHub MCP backend can perform the automatic read operations
described in `skills/infra-keeper/references/github-workflow.md` against this repository, and record
which write capabilities remain unexercised. This complements `tests/hermes-smoke-test.md`, which
covers the GitHub CLI backend.

## Backend selection

`skills/infra-keeper/references/github-backends.md` prefers an available, authenticated GitHub MCP
connection. MCP tools were present in the session, so the CLI backend was not used, not as a fallback
and not for any capability gap. `gh`, Git and direct HTTP calls were not invoked at any point.

## Operations performed before this record was created (all read-only)

| # | MCP tool | Request | Result |
| --- | --- | --- | --- |
| 1 | `mcp__github__get_me` | — | Authenticated as `NingAloha` (id 244903781); `public_repos` 8 |
| 2 | `mcp__github__list_commits` | `owner/repo`, `sha=main`, `perPage=1` | HEAD `09f4ad2`, committed 2026-10-21T22:22:35Z |
| 3 | `mcp__github__get_file_contents` | `README.md` | 2463 bytes, blob SHA `4e54eddb698936354cb495793768acda1db642dc` |
| 4 | `mcp__github__get_file_contents` | `skills/infra-keeper/SKILL.md` | Blob SHA `6f89d34e5987640712f7fbe2fe3afea40e02f142` |
| 5 | `mcp__github__get_file_contents` | `skills/infra-keeper/references/github-mcp.md` | Blob SHA `3a88a9cd0079bb60df4c6a3913eaf875579453e6` |
| 6 | `mcp__github__get_file_contents` | `tests` | One entry: `tests/hermes-smoke-test.md`, 2439 bytes |
| 7 | `mcp__github__get_file_contents` | `tests/hermes-smoke-test.md` | Blob SHA `497c55682faca19ea8c693e162b412cbd444a502` |
| 8 | `mcp__github__get_file_contents` | `tests/hermes-mcp-smoke-test.md` | Error: path does not exist in the repository — no prior file at this path |

## Verified read capability

- Identity and authentication state of the connected account.
- Single-file fetch by path on the default branch, with blob SHA for version checks.
- Directory listing for a path.
- Branch commit history, plus `main` HEAD resolution.

Not exercised in this test: file/path search, content search, diffs and comparisons, commit status
checks. Absence of evidence for those operations is not evidence that they are unavailable.

## Unverified write capability

Pre-commit checks were possible, but no write had been attempted at the time this record was
authored. The following remain unverified until a separately approved change is made and read back:

- `mcp__github__create_or_update_file` creating a new file without a blob SHA.
- Replacing an existing file with `sha` supplied.
- Whether commit-level side effects occur once per file or once per approval for a multi-file change.
- Delete or move operations (a move requires coordinated delete/create; no atomic multi-file commit
  tool was confirmed).

Creating this file is itself the only mutation in this test. Its own success is not asserted here;
it is confirmed by reading the commit and the path back after approval, and that outcome is reported
in the session that made the change rather than committed a second time into this document.

## Observations

- All read operations exercised in this test succeeded over MCP without using the CLI.
- Creating this file was proposed with full content, verification and rollback plan, and is committed
  only after explicit per-change approval; a general permission policy does not substitute for it.
- No branch was created, no pull request opened, no force-push issued, and no repository setting,
  visibility or permission was changed.

## Limitations

- Only the operations listed above were exercised. Write behaviour, search and diff capabilities are
  unverified, as noted above.
- This record documents an integration test of documentation tooling. It is not evidence of runtime
  or infrastructure health, and no infrastructure took part in the test at any stage.

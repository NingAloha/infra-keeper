# GitHub CLI smoke test — Hermes Desktop

**Date:** 2026-10-22 (CST)
**Repository:** `NingAloha/infra-keeper`
**Branch:** `main`
**Pre-test HEAD:** `cfd7a4a5225d07b923f3ea0dfa56e14403b8d693` (state observed before this record was created; not the HEAD of the commit that adds this file)
**Backend:** local GitHub CLI (`gh` 2.101.0), authenticated via OS keyring. Credentials are not recorded here.
**Scope:** repository documentation only. No live infrastructure was contacted, inspected, or modified.

## Purpose

Confirm that the InfraKeeper Skill's GitHub CLI backend can perform the automatic read operations
described in `skills/infra-keeper/references/github-workflow.md` against this repository, and that the main-only
write-approval flow is followed by Hermes Desktop as the client.

## Operations performed before this record was created (all read-only)

| # | Command | Result |
| --- | --- | --- |
| 1 | `gh auth status` | Authenticated to github.com; scopes `gist`, `read:org`, `repo`, `workflow` |
| 2 | `gh repo view --json` | Public repository, default branch `main` |
| 3 | `gh api .../contents/skills/infra-keeper/SKILL.md` | 2899 bytes retrieved |
| 4 | `gh api .../contents/skills/infra-keeper/references/github-workflow.md` | 3169 bytes retrieved |
| 5 | `gh api .../contents/README.md` | Retrieval succeeded |
| 6 | `gh api .../commits/main` | Pre-test HEAD `cfd7a4a`, committed 2026-10-21T22:16:47Z |
| 7 | `gh api .../contents/` and `.../contents/skills` | Root and `skills/` trees listed |
| 8 | `gh api .../contents/tests` | HTTP 404 — no `tests/` directory existed before this record |

## Observations

- All documented automatic operations (metadata, file contents, path listing, history) worked over
  `gh` without additional scopes.
- Creating this file is a mutation, so it was proposed with full content, verification and rollback
  plan, and is committed only after explicit per-change approval; a general permission policy does not
  substitute for that approval.
- No branch was created, no pull request opened, no force-push issued, and no repository setting,
  visibility or permission was changed.

## Limitations

- No GitHub MCP connection was configured for this test, so only the CLI backend was exercised.
- This record documents an integration test of documentation tooling. It is not evidence of runtime
  or infrastructure health, and no infrastructure took part in the test at any stage.

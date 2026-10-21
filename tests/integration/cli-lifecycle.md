# CLI lifecycle test — dedicated fixture

**Repository:** `NingAloha/infra-keeper`
**Branch:** `main` (direct commits; no branch, no pull request)
**Backend:** GitHub CLI (`gh`) only, through the REST Contents API. No GitHub MCP, no other GitHub client, no local Git push.
**Scope:** repository documentation only. No live infrastructure was contacted.
**Fixture status:** dedicated test file. It is the only path this test may create, update or delete.

## Purpose

Exercise the `gh` / Contents API write lifecycle that the MCP lifecycle test left unverified for
this backend: creation, an update conditioned on the blob SHA, the agent's own stop-on-change
guard, a stale-SHA negative test, a delete that is conditioned on the blob SHA, and restoration
by a new commit.

## Stage log

| Stage | Operation | Expected commits |
| --- | --- | --- |
| A | Create this file at v1 | 1 |
| B | Update v1 -> v2 using the v1 blob SHA | 1 |
| C-1 | Operator edits this file outside the agent after the diff was approved; the agent re-reads, compares the blob SHA and stops without issuing any write | 1 (operator) |
| C-2 | Negative test: the stale v1 blob SHA is resubmitted with content identical to the current file; the Contents API must reject it | 0 |
| D | Delete this file with the blob SHA as a precondition | 1 |
| E | Restore the pre-delete content byte for byte by a new commit | 1 |

C-1 and C-2 are separate assertions. C-1 tests the agent's guard and must produce no agent write
call at all. C-2 tests server-side rejection and is proposed separately, so a C-2 result cannot be
mistaken for a C-1 pass. C-2 sends content byte-identical to the current file, so a hypothetical
failure to enforce would produce a no-op commit rather than an overwrite.

## Conditional-update mechanism on this backend

`PUT /repos/{owner}/{repo}/contents/{path}` accepts `sha`, documented as the blob SHA of the file
being replaced and required when updating an existing file; `409 Conflict` is a documented
response. `DELETE /repos/{owner}/{repo}/contents/{path}` requires `sha`, the blob SHA of the file
being deleted, and also documents `409 Conflict`. Both operations are therefore conditionable at
the server that creates the commit, unlike the MCP delete tool, which accepts no version parameter.

Documented behavior is a contract, not an observation. Enforcement is verified empirically in
stage B (matching SHA accepted) and stage C-2 (stale SHA rejected).

## Version checks

| Version | Blob SHA | Recorded at |
| --- | --- | --- |
| v1 | 16907d8efbf835d15f8f5461774f0f139af6ff16 | stage A |
| v2 | pending | stage C-1 |
| v3 (operator) | pending | stage C-1 |

## Stage A result

Creation sent no `sha` in the request body, so the endpoint treated the call as a new file. `main`
advanced from `b9c9845d200fa3c7a396f89ea940f1e0ec2a4632` to
`5d350208272823d861b42b93b6d79ad4b3cd538b` in one commit, whose `files` array holds this path only
(`status: added`, `+63/-0`). Author and committer are both `NingAloha`, which distinguishes a
CLI-originated commit from a web-editor commit made by `web-flow`.

The byte-level check read the file back through the raw media type: 3229 bytes with SHA-256
`d609629209285f514907dc8e239a8ed33dbb8c15c170699c1eff039619018834`, identical to the approved
draft, and the returned blob SHA `16907d8efbf835d15f8f5461774f0f139af6ff16` matched the value that
had been computed locally before the write.

Stage B has not been executed. No `sha` precondition has yet been exercised against this endpoint,
and no stale-SHA rejection has been attempted.

## Constraints observed

- No force-push, no history rewrite, no branch, no pull request, no repository setting change.
- No local Git write path: the `gh` Contents API commits directly to `main`.
- No file outside this path is created, modified or deleted.
- Every mutation required separate approval of its exact diff and content hash.
- Content is restored byte for byte, so the restored blob SHA must equal the pre-delete blob SHA
  while the commit SHA must differ.

## Limitations

## External concurrent edit — C-1

This line was added through the GitHub web editor to test InfraKeeper's CLI approval-window concurrency guard.
This record documents GitHub documentation tooling only. It is not evidence of runtime or
infrastructure health.

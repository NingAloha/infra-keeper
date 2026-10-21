# MCP lifecycle test — dedicated fixture

**Repository:** `NingAloha/infra-keeper`
**Branch:** `main` (direct commits; no branch, no pull request)
**Backend:** GitHub MCP only. The agent used no GitHub CLI, no Git and no other GitHub client.
**Scope:** repository documentation only. No live infrastructure was contacted.
**Fixture status:** dedicated test file. It is the only path this test may create, update or delete.

## Purpose

Exercise the GitHub MCP write lifecycle that the earlier smoke tests left unverified:
existing-file update guarded by a blob SHA, the agent's own concurrent-edit guard,
GitHub-side stale-SHA rejection, deletion, and restoration by a new commit.

## Stage log

| Stage | Operation | Expected commits |
| --- | --- | --- |
| A | Create this file at v1 | 1 |
| B | Update v1 -> v2 using the v1 blob SHA | 1 |
| C-1 | Operator edits this file in the GitHub web editor after the approved diff was prepared; the agent re-reads, compares the blob SHA and stops without calling any write tool | 1 (operator) |
| C-2 | Negative test: the same stale blob SHA is then resubmitted to `create_or_update_file`; GitHub must reject it | 0 |
| D | Delete this file | 1 |
| E | Restore the pre-delete content by a new commit | 1 |

C-1 and C-2 are separate assertions. C-1 tests the agent's stop-on-change guard and must
produce no agent write call at all. C-2 tests the server-side rejection and is proposed
separately, so a C-2 result cannot be mistaken for a C-1 pass.

## Version checks

| Version | Pre-image blob SHA | Recorded at |
| --- | --- | --- |
| v1 | _filled in by stage B_ | stage B |
| v2 | _filled in by stage C-1_ | stage C-1 |
| v3 (operator) | _filled in by stage C-1_ | stage C-1 |

## Known control gap: deletion has no SHA guard

`mcp__github__delete_file` accepts `owner`, `repo`, `path`, `message` and `branch` only.
It exposes no blob SHA parameter, so a delete cannot be conditioned on the version the
agent last read. Any concurrent edit landing between the pre-delete read and the delete
call would be removed without detection. Mitigation is procedural only: read immediately
before deleting, record the pre-delete blob SHA and content digest, and verify the
resulting commit's file list. Residual risk is accepted for this fixture and recorded in
the test report; it is not eliminated by this test.

## Constraints observed

- No force-push, no history rewrite, no branch, no pull request, no repository setting change.
- No file outside this path is modified; no other file is deleted.
- Every agent mutation required separate approval of its exact diff.
- Content is restored byte for byte, so the restored blob SHA must equal the pre-delete
  blob SHA while the commit SHA must differ.

## Limitations

This record documents GitHub documentation tooling only. It is not evidence of runtime
or infrastructure health.

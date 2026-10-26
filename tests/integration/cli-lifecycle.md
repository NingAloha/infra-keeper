# CLI lifecycle test — dedicated fixture

**Repository:** `NingAloha/infra-keeper`
**Branch:** `main` (direct commits; no branch, no pull request)
**Backend:** GitHub CLI (`gh`) only, through the REST Contents API. No GitHub MCP, no other GitHub client, no local Git push.
**Scope:** repository documentation only. No live infrastructure was contacted.
**Fixture status:** dedicated test file. It is the only path this test may create, update or delete.

## Purpose

Exercise the `gh` / Contents API write lifecycle that earlier checks left unverified for this
backend: creation, an update conditioned on the blob SHA, the agent's own stop-on-change
guard, a stale-SHA negative test, a delete that is conditioned on the blob SHA, and restoration
by a new commit.

## Stage log

| Stage | Operation | Commits produced |
| --- | --- | --- |
| A | Create this file at v1 | 1 |
| B | Update v1 -> v2 using the v1 blob SHA | 1 |
| C-1 | Operator edits this file in the web editor after the diff was approved; the agent re-reads, compares the blob SHA and stops without issuing any write | 1 (operator) |
| C-2 | Negative test: the stale v2 blob SHA resubmitted with content identical to the current file | 0 |
| D | Delete this file with the blob SHA as a precondition | 1 |
| E | Restore the pre-delete content byte for byte by a new commit | 1 |

All six stages completed. Five write calls were sent: four produced commits (A, B, D, E), one was
rejected (C-2), and C-1 produced no agent write call at all.

## Version checks

| Version | Blob SHA | Bytes | Recorded at |
| --- | --- | --- | --- |
| v1 | 16907d8efbf835d15f8f5461774f0f139af6ff16 | 3229 | stage A |
| v2 | b49bcce63c402b70e0a0b5e35dd9d3e450abb83b | 4178 | stage B |
| v3 (operator) | f066ac51c6d3161ad9558a77834c07aca07cf156 | 4326 | stage C-1 |

The version that carries this paragraph has no row: its blob SHA does not exist until the commit
containing it is created. It is recorded in the closure report instead.

## Stage A — create

The request body carried `message`, `content` and `branch`, and no `sha`, so the endpoint treated
it as a new file. `main` advanced from `b9c9845d200fa3c7a396f89ea940f1e0ec2a4632` to
`5d350208272823d861b42b93b6d79ad4b3cd538b`: one commit, `status: added`, `+63/-0`, one path.
Author and committer are `NingAloha`, which distinguishes a CLI-originated commit from a
web-editor commit made by `GitHub`.

Reading the file back through the raw media type returned 3229 bytes with SHA-256
`d609629209285f514907dc8e239a8ed33dbb8c15c170699c1eff039619018834`, identical to the approved
draft, and the returned blob `16907d8efbf835d15f8f5461774f0f139af6ff16` matched the value computed
locally before the write.

## Stage B — update conditioned on the blob SHA

The request carried `sha` = `16907d8efbf835d15f8f5461774f0f139af6ff16`, read from `main`
immediately before the call. `main` advanced from `5d350208272823d861b42b93b6d79ad4b3cd538b` to
`05a7c7f8c7d84d82890b29f047f035a781808b0e`: one commit, `status: modified`, `+17/-1`, one path.
The resulting blob `b49bcce63c402b70e0a0b5e35dd9d3e450abb83b` (4178 bytes, SHA-256
`7f132c043c08056e570d70d1bb4419c8d4f59cac26ec62ddfde9cf22822c8675`) equalled the value computed
before the write.

A matching `sha` being accepted does not by itself show that a stale one is rejected. That is a
separate assertion, tested in stage C-2.

## Stage C-1 — concurrent edit inside the approval window

After the v3 draft was approved but before any write, the operator edited this file in the GitHub
web editor (commit `ed63fad49e650bccd1ef96d8c0ca2989924b2d6e`, `+3/-0`, committer `GitHub`). The
pre-write re-read returned blob `f066ac51c6d3161ad9558a77834c07aca07cf156` (4326 bytes) where the
approved baseline was `b49bcce63c402b70e0a0b5e35dd9d3e450abb83b`, and `main` had moved to
`ed63fad4…` from the approved `05a7c7f8…`. The agent stopped, sent **no** write request, and did
not adopt the newer identifier. The approved v3 draft was discarded without being committed.

This stage tests the client-side guard only. It says nothing about what the server would have done
with the stale request.

## Stage C-2 — stale blob SHA must be rejected

The request deliberately carried the obsolete `sha` `b49bcce63c402b70e0a0b5e35dd9d3e450abb83b`
while the file on `main` was `f066ac51…`. To keep a failed assertion harmless, the body was
byte-identical to the current file, so even a server that ignored `sha` could not have replaced
the operator's edit with different content.

Result: `HTTP/2.0 409 Conflict`, with body
`{"message":"tests/integration/cli-lifecycle.md does not match b49bcce63c402b70e0a0b5e35dd9d3e450abb83b","status":"409"}`.
The response carried `Server: github.com`, `X-Github-Request-Id` and
`X-Github-Api-Version-Selected`, so the rejection came from the API rather than from a client-side
pre-check. Afterwards `HEAD` was still `ed63fad4…`, the blob was
still `f066ac51…`, the raw bytes hashed to the same digest and the commit count was unchanged: the
rejected request produced no observable repository changes in this test.

Byte-identical content reduces the risk of damage; it does not make an unexpected success
side-effect free. A success would still have advanced `HEAD` and added a commit.

## Stage D — delete conditioned on the blob SHA

The pre-delete snapshot was 4326 bytes, SHA-256
`b97747cbb2f8d00eaaaa291558b8958923daa6bb281cad99bc91da6216e8b3d1`, blob
`f066ac51c6d3161ad9558a77834c07aca07cf156`, and the DELETE request carried that blob as `sha`.
Result `HTTP/2.0 200 OK`; `main` advanced from `ed63fad49e650bccd1ef96d8c0ca2989924b2d6e` to
`95b3d34b9ecde11fac08256c06b8504b5f3ba295`: one commit, `status: removed`, `+0/-82`, one path. The
path then returned 404 and the unrelated fixture file was unchanged.

This shows that a delete carrying a **matching** identifier succeeds. It does not show that a
delete with a stale identifier is rejected; that negative delete was deliberately not attempted,
because a failed assertion on this endpoint would have removed a path.

## Stage E — restore by a new commit

The restore request carried `message`, `branch` and the snapshot's 4326 bytes as `content`, and no
`sha`, because the path no longer existed. Result `HTTP/2.0 201 Created`; `main` advanced from
`95b3d34b9ecde11fac08256c06b8504b5f3ba295` to `343b25faf305dbc9514da12330c73965171156ce`: one
commit, `status: added`, `+82/-0`, one path.

The restored blob `f066ac51c6d3161ad9558a77834c07aca07cf156` and the restored bytes (SHA-256
`b97747cbb2f8d00eaaaa291558b8958923daa6bb281cad99bc91da6216e8b3d1`) are identical to the
pre-delete snapshot, and the commit's tree `29128a0c7f619b280fff2b6ed6e4c1ae6243034a` is the same
tree the file belonged to before deletion, while the commit SHA differs. Content was restored by a
new commit, not by rewriting history.

## Conditional-update mechanism on this backend

`PUT /repos/{owner}/{repo}/contents/{path}` accepts `sha`, the blob SHA of the file being replaced;
`DELETE` on the same path requires `sha` for the file being deleted, and both endpoints document
`409 Conflict`. Stages B and C-2 together show that on this endpoint the identifier is enforced by
the server that creates the commit: a matching value is accepted, and the stale value tested in
C-2 was rejected without observable repository changes.

Verified here: `sha` is required to replace an existing file and is enforced server-side (B, C-2);
the C-2 rejection produced no commit, no new `HEAD` and no change to the file bytes; a delete
carrying a matching `sha` succeeds (D).

Not verified here: whether a **stale** `sha` is also rejected on `DELETE`, since only the matching
case was run; concurrent sessions other than one operator edit; multi-file or atomic commits;
move/rename; permission-denied behaviour.

## Constraints observed

- No force-push, no history rewrite, no branch, no pull request, no repository setting change.
- No local Git write path: the `gh` Contents API commits directly to `main`.
- No file outside this path was created, modified or deleted.
- Every mutation required separate approval of its exact diff and content hash.
- No write was retried with a refreshed version identifier; a detected conflict ended the attempt.

## External concurrent edit — C-1

This line was added through the GitHub web editor to test InfraKeeper's CLI approval-window concurrency guard.

## Limitations

This record documents GitHub documentation tooling only. It is not evidence of runtime or
infrastructure health. It covers one public repository, one operator and one manual run per stage;
it is not an automated conformance test.

# Main-only GitHub workflow

These are the **default InfraKeeper permissions**; actual actions remain subject to platform and repository access controls.

| Operation | Default |
| --- | --- |
| Read repository metadata, paths, files, Git history | Automatic |
| Search repository content; view commits and checks | Automatic |
| Create or edit documents; append maintenance records | Explicit approval before action |
| Update multiple related documents | Explicit approval before action |
| Move/rename/delete documents or retire records | Explicit approval before action |
| Make a new corrective/revert commit | Explicit approval before action |
| Create/manage branches; create/merge PRs | Disabled |
| Force-push or rewrite history | Disabled |
| Change repository settings, visibility or permissions | Disabled |

## Read-first procedure

1. Resolve target repository and `main`. If it has no `main`, do not create or alter branches automatically; ask for an appropriate path forward.
2. Read the root README/inventory, target device index and relevant service, system, network and route records.
3. Read available history where chronology or conflicting records matter.
4. Separate documented facts, newly reported information, verified observations and unresolved assumptions.
5. Present findings without implying runtime verification.

## Propose a mutation

Before *any* repository mutation:

1. Identify the target repository, `main`, every affected path, and whether it will be created/updated/deleted/moved.
2. Fetch affected files and record their current versions; determine dependencies and cross-file consistency.
3. Prepare an explicit proposed diff or complete proposed content for creation.
4. Check for secrets and sensitive topology; identify the source and date of each factual claim.
5. Explain purpose, impact, verification, and rollback via a new commit.
6. **Ask the user to approve the specific change.** A prior general permission policy is not per-change approval.

Do not mutate before approval. A substantive change to the approved scope or diff requires renewed approval.

## Execute approved change

1. Re-read the current `main` state and relevant file versions to avoid overwriting concurrent edits.
2. If anything conflicts, stop, explain the difference, and revise the plan; seek approval again when needed. Never resubmit the rejected write with a refreshed version identifier.
3. Apply only the approved changes to `main`. Prefer atomic multi-file commits if the selected GitHub backend supports them. Never use force-push.
4. If a partial multi-file update occurs, report exactly which files changed and which failed. Any repair is a separate mutation and needs approval if not covered by the original approved plan.
5. Read back the resulting commit and all affected files; compare with the approved result.
6. Report commit identifier, verified changes, remaining gaps, and the fact that runtime state was **not** validated by this step.

## Version checks before writing

1. Read each file's version identifier from the same branch you will write to, immediately before the write.
2. Distinguish the operation before deciding what the identifier means:
   - **Creating a new path.** There is no pre-image to condition on. The review that matters is whether the path should be created at all; a version check cannot guard it.
   - **Updating an existing path.** Supply the version identifier required by the backend for a conditional update. If the backend does not support or receive such a precondition, do not assume the update is protected against concurrent modification; its behavior must be verified.
   - **Deleting or moving a path.** If the backend accepts no identifier for the operation, it cannot be made conditional at all. See [Backends without conditional delete](#backends-without-conditional-delete).
3. Backends differ in parameter names and semantics (`sha`, blob SHA, `ref`, expected-version token) and some accept none of them. Read the tool's actual schema instead of assuming that a familiar field name implies the same guarantee.
4. Treat the identifier as evidence of what you read, not as a lock.

## Where the check is enforced

A conditional update protects the write only if the enforcing side is the server that commits. In that case a version mismatch is rejected and the rejected write changes nothing — it is atomic with respect to the version.

A re-read performed by the client immediately before writing is a different mechanism. It narrows the window but cannot close it: the version can change between the read and the commit, and the client-side re-read alone cannot guarantee rejection.

A successful call does not tell you which of the two you received, and an error message does not always make it clear either. Report a client-side pre-read as a pre-read, never as a server-side check, and do not describe the two as equivalent safeguards.

Measured once: an update through the GitHub REST Contents API (CLI backend) was rejected by the
API itself with `409`, and the response carried `Server: github.com` and a GitHub request ID. That
rejected write produced no commit. This is the server-side case above. The same repository's MCP
path produced a prose rejection whose layer was not identified, so the two backends still support
different claims.

## After a conflict

A rejected write is a conflict signal, not a retry signal.

1. Stop. Report the version you prepared against and the version now present, quoting the backend message accurately.
2. Do not resubmit with the refreshed identifier. That would overwrite the concurrent change while making the overwrite look like an ordinary update.
3. Do not treat backend advice to "refresh the version and retry" as authorization.
4. Re-read the current content, prepare a new diff against it, and obtain new approval; the earlier approval was scoped to the earlier base version.
5. State in the report whether the rejection came from the backend or was caught by your own pre-write comparison. These are different guarantees and must not be merged.

## Backends without conditional delete

Some backends expose delete without accepting a version identifier. The GitHub MCP `delete_file` tool is one: it accepts `owner`, `repo`, `path`, `message` and `branch` only.

- Such a delete cannot be conditioned on the version you read, and no amount of re-reading removes that. An edit landing between the read and the delete is removed without anything rejecting the operation.
- The consequence is about approval, not forensics: the latest file state can be deleted without a fresh approval, even though the approval you obtained described a version that no longer existed. Earlier versions remain in the commit history and can be restored by a new commit.
- Re-reading immediately before deleting, and verifying the resulting commit's file list afterwards, are **detection** measures. They do not prevent the deletion and must not be described as an atomicity guarantee.
- State this residual risk in the approval request before deleting, and repeat it in the report afterwards.

Not every backend shares this gap. The GitHub REST Contents API requires `sha` on delete, and a
delete carrying a matching value has been observed to succeed. Whether it rejects a stale value has
not been tested, so the presence of the parameter must not be read as a guarantee that a stale
delete would be refused.

## Recovery

Use a new, explicitly approved corrective commit to restore prior content. Do not rewrite Git history or reset the remote branch. If permission or platform safety blocks an operation, report it and stop rather than changing execution channels.

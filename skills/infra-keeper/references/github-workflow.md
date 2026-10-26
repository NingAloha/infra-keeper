# Isolated device-branch GitHub workflow

These are the **default InfraKeeper permissions**; actual actions remain subject to platform and repository access controls.

The selected repository must be owned by the authenticated GitHub user. Organization repositories,
collaborator repositories and repositories owned by another user are outside the scope of this
workflow, even when GitHub grants the account access.

| Operation | Default |
| --- | --- |
| Read repository metadata, paths, files, Git history | Automatic |
| Search repository content; view commits and checks | Automatic |
| Create or edit documents on the bound device branch | Explicit task-scoped conversational authorization; no duplicate approval |
| Update multiple related documents | One explicit approval covering the related bounded task |
| First-run create one personal private repository | One separate explicit bootstrap approval; no repeat on later setup runs |
| Create the bound device branch | Explicit task-scoped approval covering the documentation task |
| Move/rename/delete documents or retire records | Fresh separate approval |
| Make a new corrective/revert commit | Fresh explicit approval |
| Force-push or rewrite history | Disabled |
| Change repository settings, visibility or permissions | Disabled |

## Read-first procedure

1. Resolve target repository and canonical `main`. If it has no `main`, do not create or alter branches automatically; ask for an appropriate path forward. When the task discusses a device, resolve and activate only that device's stored branch; do not synchronize other device branches.
2. Read the root README/inventory, target device index and relevant service, system, network and route records.
3. Read available history where chronology or conflicting records matter.
4. Separate documented facts, newly reported information, verified observations and unresolved assumptions.
5. Present findings without implying runtime verification.

## Conversation-scoped authorization for documentation writes

An **explicit user instruction in the current conversation** can authorize a bounded documentation write; a separate last-minute "may I commit?" exchange is **not** required if the user has already confirmed the repository, intended paths or unambiguous device scope, the intended result, and relevant risks. Do not confuse a user approving a device command with approval to write GitHub, or a user's technical question with a request to edit documents.

- **Authorized without a second prompt:** "Record the just-verified Ruby version for mba-m4-01", "Update those two documentation files as we discussed", or approval of a concrete proposed creation/update. Resolve target paths from the existing binding and device context; read their latest content; perform only the naturally implied, evidenced, low-risk documentation edit. Explain the change briefly before writing when its details are not already visible. A diff need not become an extra confirmation ceremony.
- **Not authorized:** merely supplying terminal output, asking what a result means, discussing an installation plan, generic standing access, or saying that the agent may maintain everything indefinitely. Prepare a specific proposal and ask once.
- **Always separately confirm:** deleting or retiring records, moving/renaming files, bulk restructuring, rebinding repositories, expanding to additional devices/repos, materially changing the approved plan, or writing sensitive or consequential information. Never store secrets even with approval.
- **Scope:** authorization applies to the task as described, including the necessary related documentation files, and expires when that task is completed or materially changes. For a multi-file task, one clearly scoped approval covers the related writes; never insist on one approval per file. If approval names only one path, do not silently add others.
- **Safeguards independent of approval:** check `main`, current branch HEAD and file versions, apply backend-supported preconditions, guard against accidental creation/overwrite, review sensitive data, verify commits and contents, and report partial writes. If baseline changes during preparation, stop and re-evaluate under the conflict rules.

## Propose a mutation

Before a repository mutation:

1. Resolve the bound target repository, `main`, affected paths and operation types.
2. Read current files, versions, relevant links and the new user-provided evidence.
3. Prepare the exact content/diff or a precise bounded change summary; check for secrets and distinguish observed facts from reported or intended changes.
4. Decide whether the user **already explicitly authorized** this bounded documentation edit in the conversation. If yes and the scope/risk has not changed, proceed without asking again. Otherwise show the proposed scope, evidence, risk/rollback and **ask once** before writing.
5. If there is a material ambiguity, deletion, migration or changed target, pause for fresh approval. No authorization overrides repository/backend denials or platform permissions.

## Detailed Git commit messages

Git history is the maintenance log. Do **not** add a separate running `operations.md` or append a changelog to each Markdown page. Each commit must describe the **documentation changes in that actual commit**, not conflate them with device commands that the user ran.

- Use a specific Conventional Commit-style subject such as `docs(mba-m4-01): verify Ruby runtime and RubyGems`. Avoid generic `docs: update` or invented operational claims such as `install Ruby` if the commit only records existing software.
- Include a meaningful body, proportional to the change, with: **Changes** (precise fields, before/after where relevant); **Evidence** (user-supplied output/report, observation date and test level); **Pending / limitations** (only relevant outstanding facts); and **Scope / impact** (documentation-only, affected file(s) where useful). For a trivial one-field edit, two or three body lines may suffice; for registration or cross-file changes, provide a detailed structured body.
- State device-operation timing only when evidence establishes it. Git timestamp is the documentation commit time, **not** when software was installed or updated.
- Prefer one coherent commit for a logical task when backend capabilities support atomic multi-file writes. Where a backend forces per-file commits, write individually accurate messages tied by a clear shared task description; never claim an atomic multi-file update. Report failures and partial completion.
- Do not embed credentials, secret output, personal identifiers or unnecessary sensitive topology in a commit message; history is durable and may be public or hard to retract.

## Mandatory pre-write validation gate

This gate is part of every approved documentation transaction, not an optional audit report. Follow [audit lessons](audit-lessons.md) for evidence levels and BLOCK/WARN/PASS disposition.

1. **Define scope:** enumerate every authorized target file and operation, including planned forward-reference targets. Read current versions and identify concurrent changes; verify authorization and repository/branch.
2. **Validate the candidate before mutation:** inspect supported claims and timestamps, privacy/secrets, exact permitted paths, syntactic Markdown links and filename-like references (including inline code and table cells). Resolve relative paths from the *source Markdown directory*. Reject unexpanded concrete-path placeholders. A target not yet on GitHub is permissible only if it is in the explicit approved batch target set; by batch closure it must exist.
3. **Enforce BLOCK:** any in-scope unresolved reference, missing promised target, unsupported material conclusion, unauthorized edit, secret exposure, or conflict aborts the write. Logging an error and continuing is forbidden. Repair candidate material within existing approval only when its meaning and scope remain authorized; otherwise request new approval.
4. **Handle WARN separately:** report pre-existing failures outside task scope without silently changing them. Run a repository-wide check when practicable but never conflate its result with acceptance of changed/affected files. A known out-of-scope broken link is not permission to expand edits.
5. **Commit and verify:** only after PASS, submit the approved update to the active device branch with backend-supported version preconditions; read back the branch contents, compare to the prepared candidate, re-check changed/affected links, and update only that branch's local checkpoint. A failed branch write or local-state update is a reported partial failure, not grounds for an unauthorized repair. The first-run repository bootstrap is a separate creation transaction and must be verified before binding.
6. **Report exact units:** commits, changed files, correction commits, corrected issues and remaining failures are distinct counts. Separate task validation, optional whole-repository validation and runtime/service acceptance.

A pre-write local or agent-side check never supplies a server-side concurrency guarantee. Continue using the conditional-update/conflict rules below.

## Execute approved change

1. Re-read the current `main` state, activate and then re-read the bound device-branch head, and read relevant file versions to avoid overwriting concurrent edits.
2. If anything conflicts, stop, explain the difference, and revise the plan; seek approval again when needed. Never resubmit the rejected write with a refreshed version identifier.
3. Apply only the approved changes to the active device branch. Never write documentation directly to `main`, merge device branches, or use force-push.
4. If a partial multi-file update occurs, report exactly which files changed and which failed. Any repair is a separate mutation and needs approval if not covered by the original approved plan.
5. Read back the resulting commit and all affected files; compare with the approved result.
6. Report commit identifier, verified changes, remaining gaps, and the fact that runtime state was **not** validated by this step.

## Version checks before writing

1. Read each file's version identifier from the same branch you will write to, immediately before the write.
2. Distinguish the operation before deciding what the identifier means. Every create, update or delete
   through the bundled helper must include the current target-branch HEAD as a precondition:
   - **Creating a new path.** There is no file pre-image to condition on, so the target-branch HEAD is the required concurrency precondition. The review still determines whether the path should be created at all.
   - **Updating an existing path.** Supply the version identifier required by the backend for a conditional update. If the backend does not support or receive such a precondition, do not assume the update is protected against concurrent modification; its behavior must be verified.
   - **Deleting or moving a path.** If the backend accepts no identifier for the operation, it cannot be made conditional at all. See [Backends without conditional delete](#backends-without-conditional-delete).
3. Backends differ in parameter names and semantics (`sha`, blob SHA, `ref`, expected-version token) and some accept none of them. Read the tool's actual schema instead of assuming that a familiar field name implies the same guarantee.
4. Treat the identifier as evidence of what you read, not as a lock.

## Where the check is enforced

A conditional update protects the write only if the enforcing side is the server that commits. In that case a version mismatch is rejected and the rejected write changes nothing — it is atomic with respect to the version.

A re-read performed by the client immediately before writing is a different mechanism. It narrows the window but cannot close it: the version can change between the read and the commit, and the client-side re-read alone cannot guarantee rejection.

A successful call does not tell you which of the two you received, and an error message does not always make it clear either. Report a client-side pre-read as a pre-read, never as a server-side check, and do not describe the two as equivalent safeguards.

Measured once: an update through the GitHub REST Contents API (via `gh`) was rejected by the API
itself with `409`, and the response carried `Server: github.com` and a GitHub request ID. That
rejected write produced no commit.

## After a conflict

A rejected write is a conflict signal, not a retry signal.

1. Stop. Report the version you prepared against and the version now present, quoting the backend message accurately.
2. Do not resubmit with the refreshed identifier. That would overwrite the concurrent change while making the overwrite look like an ordinary update.
3. Do not treat backend advice to "refresh the version and retry" as authorization.
4. Re-read the current content, prepare a new diff against it, and obtain new approval; the earlier approval was scoped to the earlier base version.
5. State in the report whether the rejection came from the backend or was caught by your own pre-write comparison. These are different guarantees and must not be merged.

## Conditional delete on the CLI backend

The GitHub REST Contents API requires `sha` on delete. The bundled CLI helper re-reads the file,
requires a matching `--expected-sha`, and sends that SHA with the delete request. A matching-value
delete has been observed to succeed. Whether GitHub rejects a stale value on `DELETE` has not been
tested, so do not present the helper's pre-read as a server-side guarantee; stop on a local mismatch
and report any server rejection accurately.

## Recovery

Use a new, explicitly approved corrective commit to restore prior content. Do not rewrite Git history or reset the remote branch. If permission or platform safety blocks an operation, report it and stop rather than changing execution channels.

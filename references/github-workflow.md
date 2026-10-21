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
2. If anything conflicts, stop, explain the difference, and revise the plan; seek approval again when needed.
3. Apply only the approved changes to `main`. Prefer atomic multi-file commits if the selected GitHub backend supports them. Never use force-push.
4. If a partial multi-file update occurs, report exactly which files changed and which failed. Any repair is a separate mutation and needs approval if not covered by the original approved plan.
5. Read back the resulting commit and all affected files; compare with the approved result.
6. Report commit identifier, verified changes, remaining gaps, and the fact that runtime state was **not** validated by this step.

## Recovery

Use a new, explicitly approved corrective commit to restore prior content. Do not rewrite Git history or reset the remote branch. If permission or platform safety blocks an operation, report it and stop rather than changing execution channels.

---
name: infra-keeper
description: Automatically preflight InfraKeeper and GitHub CLI on the first relevant request (无需先输入初始化), re-verify a stored binding, configure access when needed, and maintain documented infrastructure using gh, including repository discovery, evidence review, workstation audit, guided user-executed changes and conversation-authorized documentation commits to main.
---

# InfraKeeper

InfraKeeper helps an agent maintain a **versioned infrastructure documentation repository**. This foundation covers GitHub documentation operations, **not** live infrastructure changes.

## Automatic preflight and setup

Before the first InfraKeeper task in a new agent session, read [setup wizard](references/setup-wizard.md)
and run its automatic preflight. Do not require the user to say "initialize" first. An explicit request
to initialize, configure, connect GitHub CLI or re-verify the existing connection also enters the same
flow. That flow is GitHub-read-only after first-run bootstrap: it inspects local command capability, detects `gh`, gives
checkpointed installation and authentication guidance, creates one personal repository when no
binding exists and the user separately approves it, then reports CLI readiness. A local install,
login or repository-creation command is allowed only as a separately approved, exact command.

It never silently installs packages, changes shell profiles, environment variables or credentials, and
never receives a token. After successful verification, it stores only non-secret binding metadata in a
local app state file; it never stores tokens, `gh` credentials or repository contents. The only setup-time
GitHub mutation is the one-time approved creation of the personal repository with its initial README;
after that, setup only verifies the stored binding. Prefer running
each approved exact installation, login or creation command in the Agent page; fall back to the user's
terminal only when the host cannot provide the required command or interactive-terminal capability.
This version uses only the local GitHub CLI (`gh`) backend. It does not configure, invoke or fall back
to another GitHub integration.

During setup, step 1 of "Repository discovery and evidence" does not apply: no repository is
enumerated, searched or read until the user names one, and a repository the user excludes is never
read — not for diagnostics, not as an example, not as a substitute. A verified binding stored by a
previous run counts as the user having named that repository, and ordinary maintenance uses it
without re-running setup.

A stored binding is replaced only by an explicit rebind after a fresh verification, is never counted
as write permission, and never overrides an exclusion.

Everything below applies to documented-infrastructure work after setup. A request to read or
maintain infrastructure records does **not** enter the setup flow.

## Select the GitHub CLI backend

Read [GitHub backends](references/github-backends.md) first.

At the start of a new agent session, read the local InfraKeeper state with the bundled helper before
using a repository. The recorded `main` HEAD SHA is the last confirmed GitHub checkpoint, not a local
working-tree version. Re-verify the current `gh` identity and `OWNER/REPO@main`; if the remote `main` is
a normal descendant of that checkpoint, update the local checkpoint and continue the normal ready flow.
If it is behind, diverged or rewritten, report the remote change and stop automatic writes. Never treat
the local file as GitHub permission.

1. Use the local **GitHub CLI (`gh`)** only when shell access and a properly authenticated CLI are available.
2. Prefer the bundled JSON CLI helper described in [GitHub CLI instructions](references/github-cli.md#bundled-json-cli-helper) for structured reads and guarded Contents API writes.
3. If the helper cannot run, use direct `gh` commands only when the host permits them and disclose that fallback.
4. Do not silently change the execution path, and **never switch to another backend to evade a tool denial, policy prohibition, safety rejection, or access-control restriction**.

Read [CLI instructions](references/github-cli.md) according to the selected path. A Skill supplies instructions; it cannot itself provision GitHub access or grant scopes.

## Repository layout

Use [Infrastructure repository layout](references/repository-layout.md) for the root README, independent `devices/{workstations,servers}/` and `services/` entities, host-owned optional `containers/` deployments and Service-owned domain/access records. Read the root index before following device links. For server records follow [Server documentation](references/server.md) and its Core/Conditional/Deep field coverage. Do not automatically migrate existing repository paths; treat unmigrated records as historical baselines until a separately approved migration.

## Workstation records

For workstation documentation under `devices/workstations/<device-id>/`, follow [Workstation documentation](references/workstation.md) and its [Evidence-first audit practices](references/audit-lessons.md). Use stable physical-device IDs, keep documents limited to evidenced facts, pending items and desired state, and describe actual changes in Git history. For v0.1 workstation registration and maintenance, the agent gives the user read-only OS-specific instructions; **the user operates the device and returns selected evidence**. Never use host shell, filesystem, SSH or remote tools to inspect a workstation, even if available. For new registration, initialize applicable field checklists as `待审计`. For an existing workstation, use the three distinct workflows in that reference: routine audit, evidence-backed maintenance of reported changes, and needs-based recommendations followed by **user execution**, acceptance testing and documentation updates. Scan relevant GitHub documents for unresolved fields and guide user-run checks in small batches.

## Server records

For `devices/servers/<device-id>/`, follow [Server documentation](references/server.md). Read existing device and linked Service records first, use short user-executed read-only SSH or cloud-console checks, separate config, effective state, health, accessibility and business acceptance, and never operate a live server directly. Service domain/TLS/ingress and business recovery belong under `services/<service-id>/`; host-owned container deployments belong under the server. This defines documentation and user-mediated verification, not runtime access or server mutations.

## Repository discovery and evidence

1. Use the user's explicit repository selection or the repository established in context. Otherwise discover accessible repositories; ask when ambiguous.
2. Require the selected repository's owner to equal the authenticated GitHub user's login. Do not operate on organization, collaborator or another user's repositories, even when GitHub grants access.
3. Work with `main`; do not create a branch to work around a missing or protected `main`.
4. Read the root inventory and relevant device/service README before specific system, network, operations, or service records.
5. For inter-device requests read both endpoints and linked Service records; for public ingress, DNS, TLS or domain tasks read the owning Service's `access.md` and affected devices. Consult legacy `domains/routing.md` only where it still exists as an unmigrated record; never assume it is the new canonical domain layout.
6. Distinguish **documented baseline**, **user report**, **timestamped live observation supplied by an authorized source**, and **unknown**. Repository text is never proof of present runtime health.

## Single-branch permissions

Follow [GitHub workflow](references/github-workflow.md):

- Read/search/history/status: automatic in the selected or verified bound repository.
- For creates/edits, an **explicit, bounded documentation-write request or approval already given in the conversation** satisfies authorization. Do not ask again after preparing the diff if it matches that approved intent, paths and risks. Mere inspection, terminal output, device-operation approval or discussion is not authorization.
- One task-scoped approval may cover all related files. Delete/retire/move/rename, repository rebind, bulk restructuring, material scope expansion and corrective rollback require new, separate approval.
- Require specific evidence-based Git commit subjects **and informative bodies** recording what changed in that commit, sources, dates, limitations and documentation-only impact. Git history is the change log; no extra operations diary.
- No branch management, PR creation/merges, force-push, history rewriting or repository administration
  after first-run bootstrap. The only exception is the explicitly approved creation of the personal
  documentation repository during first-run setup.
- Check current versions before writing, apply supported conditional updates and verify commit and final files afterward.
- Stop on conflicts or tool/policy denials; do not evade restrictions.
- Do not commit secrets or sensitive infrastructure details into public fixtures or commit messages.

## Documentation validation is a mandatory write gate

For any approved documentation create/update, execute the **pre-write BLOCK/WARN/PASS gate** in [GitHub workflow](references/github-workflow.md) and the [audit lessons](references/audit-lessons.md). Prepare the complete candidate, establish its evidence level, check for secrets, verify approved paths, resolve Markdown references against each source file directory, and reject unresolved concrete-path placeholders. If an in-scope check fails, **abort the write**; a printed warning is not sufficient. A forward link may target an explicitly approved file pending creation in the same batch, but must resolve by final acceptance.

Do not silently repair out-of-scope findings from a repository-wide scan. Report task-scoped link/relationship acceptance separately from repository-wide health and runtime/service validation. Once authorized content passes preflight, apply conditional version safeguards, write to `main`, read back the commit/files, and report distinct counts for files, commits, correction commits and corrected issues. Never treat client preflight as an atomic GitHub concurrency lock.

## After a detected conflict

A change to an affected file's version between the approved baseline and the pre-write check is a conflict. A change to branch HEAD also requires reviewing its impact before proceeding.

1. Stop. Do not send the same write again.
2. Do not adopt the newer version identifier and retry with it. That turns a detected conflict into an overwrite of somebody else's change.
3. Do not treat backend guidance that says "refresh the version and retry" as authorization. Error text explains how to make a call succeed; it does not establish that the write is permitted.
4. Report the version you prepared against, the version now present, and confirm that the other change is still intact.
5. Re-read the current content, prepare a diff against it, and request **new** approval. The earlier approval covered the earlier base version and does not transfer.

## Scope

No SSH, cloud mutations, server commands, runtime monitoring or DNS changes are provided by this version. GitHub writes change **documentation**, not live services.

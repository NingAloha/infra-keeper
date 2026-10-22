# Evidence-first audit practices

This reference distills reusable **process lessons**, not hardware facts, from the 2026-10-22 `mba-m4-01` workstation registration and maintenance exercise in an isolated Sandbox. The exercise's Git history is a record of documentation edits and user-reported observations, **not** independent access to that Mac. Do not copy its versions, services, device names or personal network facts into another device record.

## Audit for useful decisions, not maximum inventory

1. Start with the bound repository, root index and existing device topics. Map initial coverage to the workstation catalog, but collect evidence in small priority-based batches. Do not make completion of every candidate field a condition for registration.
2. Before each batch ask: What conclusion will this check support? What action or documentation decision depends on it? What is the cheapest safe, privacy-preserving observation? Stop collecting when further detail would not materially improve a decision.
3. Distinguish **registration coverage**, **routine re-verification**, **troubleshooting**, **planned changes**, and **user-directed documentation cleanup**. Do not restart a complete inventory for a small follow-up.
4. A new observation can reveal an unanticipated relevant topic (e.g. system protection and background tasks). Add a justified topic and link it from the device README. Avoid adding irrelevant mandatory topics to the canonical schema.

## Evidence ladder: never promote weak evidence into certainty

Use the narrowest claim warranted:

| Evidence received from user | What it establishes | What it does not establish |
| --- | --- | --- |
| `command -v` / PATH search | Shell can or cannot resolve a command in that session | Installed/not-installed across the whole device; executable filesystem path if result is an alias/function |
| A file, symlink or application bundle exists | Presence at the inspected path; a broken link points to an absent target | That an application is functioning; when a program was installed/uninstalled |
| Tool `--version`, package inventory, a GUI screenshot | The observed version/list/interface state at a stated time | All installation paths or actual end-to-end functionality |
| Service configuration or a preference value | Configured intent or saved setting | **Effective enablement**, network routing or policy enforcement |
| Explicit state query or simple functional check | Specific queried state or tested capability at that moment | Unmeasured features, all clients/routes or persistence |
| Repeated observations / different read paths | Increased confidence in a measured value and detection of inconsistencies | The root cause of an unexplained discrepancy |

Illustrative case from the exercise: macOS firewall policy fields were initially recorded, but a separate **enablement** check later showed the firewall was disabled. Do not claim a security control is active from its settings alone. Similarly, a connected VPN service, a tunnel interface with traffic, and a proxy client's established connections are related observations, not proof of which app owns every interface or where each individual connection travels.

For negative conclusions say **“not found in the checked PATH/manager/directory”**, unless a comprehensive check and its scope are established. For aliases/functions, check via an appropriate user-run `type`/definition or executable-path test rather than treating a bare `command -v` result as a path. Treat `cargo install --list` results as scoped to the active Cargo home, and Java system discovery as scoped to paths that discovery covers.

## Contradictions and inference

- Keep conflicting observations with sources and dates until reconciled. Re-check using independent read methods when worthwhile; don't fabricate an explanation merely because values appear inconsistent.
- Mark inferred platform properties **in the value itself** as `inferred, not directly observed`, not only in a distant evidence note.
- If several legitimate tools report the same unexpected value, document that value as observed while leaving the interpretation bounded; do not silently “fix” it using expected version conventions.
- “No output”, a failed command, a missing binary, an unindexed GUI app and a permission-restricted check have different meanings. Choose alternative low-risk checks only if the answer matters.

## Device-change cleanup is a separate operation

During the exercise the user removed stale Docker/OrbStack-related symbolic links. Generalize the safe sequence:

1. Identify exact paths and inspect link targets **read-only**. Distinguish dangling links from live tools and determine whether anything still relies on them.
2. Explain the proposed mutation, its precise target set, reversibility and rollback. Obtain user consent to perform a device-side operation; the agent **must not run it**.
3. Give narrowly guarded user-run steps targeting only the verified objects. Do not suggest broad globs, recursive deletes or privilege escalation by default.
4. Have the user independently verify the intended before/after state. Record what was actually observed and whether the user reports executing a change; never imply Git updated the operating system.
5. Update all affected documentation links/summaries under a separate, bounded GitHub write authorization. Documentation approval and device-operation consent are different.

## Finish cleanly without burying uncertainty

- Maintain a small triage set: **verified/resolved**, **still actionable Pending**, **accepted limitation or not pursued at user's direction**, **confirmed non-applicable**, and **Desired**. Do not equate “not pursued” with “proved resolved”.
- A documented historical observation can remain useful while its causal explanation is left uninvestigated. Do not turn every unknowable version-string mismatch or private/sensitive check into an eternal Pending task.
- Retire duplicate, policy-blocked and low-value checklist items when the user requests slimming. Keep the meaningful evidence limitation in the topic when it changes interpretation; use Git commit bodies for collection history rather than long postmortems in Markdown.
- Before declaring an audit complete, reconcile the device README coverage/status with topic files and newly created topics; check cross-topic consistency (e.g. container leftovers removed, version updates in two topics). Check for stale summaries after a later corrective commit.
- Report **coverage complete for this agreed audit scope**, not “all software and all security properties confirmed”. Do not continue interrogating the device once the user declares the audit finished. Reopen only for a new task or material new evidence.

## Documentation and Git hygiene

- Facts belong in topic files, dated and tied to user-returned evidence; the current README is an index, not a duplicate history.
- Keep commit bodies detailed and scoped: exact changed claims, source/date, verification level, limitations, and what the agent did **not** operate. For multiple per-file commits in one logical task, describe partial scope accurately.
- Pre-write version/concurrency checks and read-back verification still apply under task-scoped conversational approval.
- Never publish secrets, private network destinations, SSH aliases, device serial numbers, proxy node names, raw configs, or unnecessary identifiers.

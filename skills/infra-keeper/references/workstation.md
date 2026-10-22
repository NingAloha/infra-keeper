# Workstation documentation

Use this reference when creating or maintaining a workstation record in the user's **already selected or verified bound repository**. This is a documentation convention, not a device scanner or permission to execute commands on a workstation.

## Layout

Use a stable, unique, lowercase device ID (letters, digits and hyphens) rather than an operating-system name. A workstation record has this conventional layout:

```text
devices/workstations/<device-id>/
├── README.md
├── system/
│   ├── hardware.md
│   └── os.md
└── environment/
    ├── shell.md
    ├── package-managers.md
    ├── languages.md
    ├── tools.md
    └── network.md
```

The README identifies the physical device, its responsibilities, a short overview, and links to available topic files. Place technical facts in the relevant topic rather than duplicating them in the README. Omit non-applicable topic files; do not create empty placeholders. Split a complex topic into extra files only when warranted.

- `system/hardware.md`: model, CPU, memory, storage, GPU and relevant hardware.
- `system/os.md`: operating system, version, build and architecture.
- `environment/shell.md`: shell, terminal and relevant non-secret environment behavior.
- `environment/package-managers.md`: installed package managers and their observed state.
- `environment/languages.md`: runtimes, compilers, SDKs and build toolchains.
- `environment/tools.md`: development applications and supporting tools.
- `environment/network.md`: network clients, proxies, VPN, SSH and remote access, with sensitive details omitted.

This layout works for macOS, Windows and Linux; platform-specific information belongs within the corresponding topic. Do not require an `operations.md` or changelog.

## What a document says

Documents describe only **Facts**, **Pending**, and **Desired**:

- **Facts**: what is known, including its evidence source, observation or verification date, and relevant uncertainty. Distinguish a detected installation, an actual functional test, and a user report. Never present a historical baseline as live monitoring.
- **Pending**: unfinished work or unresolved questions, without implying they were completed.
- **Desired**: intended configuration or outcomes, clearly separate from observed facts.

These are semantic categories, not mandatory headings. Omit empty sections; use natural headings when clearer. Keep current unresolved issues in the appropriate topic, not in an accumulated operations diary.

## User-mediated workstation interaction (v0.1)

**The agent does not operate or inspect a workstation directly.** This remains true even if the host exposes terminal, local files, SSH, remote execution, automation, or other operating-system tools. Such tools must not be used for workstation inventory or diagnosis in this version. GitHub tools are for reading and, after separate approval, updating the documentation repository only. The user runs commands, navigates GUI screens, and decides what results to share.

### First registration

When the user asks to register a new workstation:

1. Resolve the already selected or verified bound documentation repository. Read its root inventory and existing workstation IDs; never guess another repository. Do not restart the GitHub setup wizard for a normal registration request.
2. Establish whether this is a new physical device or an existing device evolving over time; obtain or propose a unique stable device ID and let the user confirm it. Ask for the operating-system family only if it is not already clear. Do not assume the agent host is the device being registered.
3. Use the layout above as a **coverage checklist**, not a questionnaire that must all be completed at once. Identify what evidence is missing and give the user small, manageable batches of read-only instructions, appropriate to their OS. Include the purpose of each command or GUI step, what to copy back, and any privacy-sensitive fields to omit. Prefer straightforward built-in OS tools; do not ask the user to install diagnostic dependencies merely to fill a document.
4. The user runs the instructions themselves and shares selected terminal output, screenshots, or descriptions. Interpret only that supplied evidence. Record its source and date and distinguish user reports, detected components and demonstrated working behavior. Never claim to have executed a check.
5. Populate supported Facts; put unresolved or deferred checks in Pending. Ask the user for Desired goals instead of inventing them. An incomplete record is acceptable: summarize coverage and the next useful, optional batch rather than blocking registration.
6. Present the proposed device tree and the complete creation/update diff, along with uncertainty and privacy review. Ask for explicit GitHub write approval under the established workflow. After an authorized write, verify the resulting commit and files; otherwise stop with the proposal.

### Maintenance of an existing workstation

Read the device README and only the relevant topic files. For a question about installed software, a reported configuration change, an unfinished task, or a desired outcome, provide targeted user-run verification steps **only when evidence is needed**. Do not re-collect the entire device inventory. Reconcile the user's supplied results with prior dated Facts, Pending and Desired; propose only the changes actually supported, and obtain separate write approval.

For questions about what remains unfinished, summarize documented Pending entries with their original evidence dates. Do not imply any item has been freshly checked.

### Instruction safety and pacing

- Prefer a short first batch (one topic or a few commands) and adapt the next batch to the user's responses. Accept partial, manual or GUI-only answers; do not demand a full template upfront.
- Make each command copyable, identify its OS and shell, and explain whether it is expected to be read-only. Avoid commands that install, delete, edit settings, restart services, change access permissions, or expose credentials. If the user wants an actual configuration change, treat it as a separately authorized task, not data collection.
- Warn the user before requesting output that may contain usernames, device identifiers, network addresses, internal paths or other personal details. Ask them to redact unnecessary fields before sharing; never request secrets, full proxy configurations, private keys or auth tokens.
- If a command fails, record the limitation and offer a safe alternative or leave the fact Pending. Do not fabricate output, insist on elevated privileges, or silently substitute a riskier command.
- Keep conversational prompts minimal: ask only for information necessary for the next useful step. Clearly separate observed Facts, unanswered Pending and user-stated Desired throughout the exchange.

## Device identity

A device ID follows continuity of the physical workstation. Incremental repairs, part replacements, hardware upgrades or OS reinstalls retain the ID, even if every component is eventually replaced over time. One-time replacement of the whole physical device creates a new ID, even if the OS and development environment are migrated unchanged. A retired device leaves the current inventory; Git history preserves the previous record. Do not rename existing device directories or migrate old layouts without a separate, approved change.

## Git history and safe maintenance

Markdown describes the current documented state (facts, pending items, desires). Git commits describe **only what actually changed in that commit**. Make clear whether the change was to documentation or to a device: a documentation edit is not evidence that an installation, repair or migration happened. Do not duplicate a running changelog in the topic documents or commit body.

Read the device README and relevant existing topics before proposing edits. Compare the new evidence with the dated baseline; do not silently discard uncertain or contradictory observations. Offer a precise diff and seek explicit approval **for every GitHub mutation** under the normal workflow. Do not change live device configuration as part of documentation maintenance.

Never commit passwords, tokens, private keys, private proxy credentials or raw sensitive configurations. Omit unneeded public connection addresses and other sensitive infrastructure details. Use the canonical `devices/workstations/<device-id>/` path for new registrations. Do not create compatibility aliases or automatically migrate existing paths; any restructuring requires separate explicit approval.

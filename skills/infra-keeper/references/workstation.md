# Workstation documentation

Use this reference when creating or maintaining a workstation record in the user's **already selected or verified bound repository**. This is a documentation convention, not a device scanner or permission to execute commands on a workstation.

## Layout

Use a stable, unique, lowercase device ID (letters, digits and hyphens) rather than an operating-system name. A workstation record has this conventional layout:

```text
devices/<device-id>/
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

## Device identity

A device ID follows continuity of the physical workstation. Incremental repairs, part replacements, hardware upgrades or OS reinstalls retain the ID, even if every component is eventually replaced over time. One-time replacement of the whole physical device creates a new ID, even if the OS and development environment are migrated unchanged. A retired device leaves the current inventory; Git history preserves the previous record. Do not rename existing device directories or migrate old layouts without a separate, approved change.

## Git history and safe maintenance

Markdown describes the current documented state (facts, pending items, desires). Git commits describe **only what actually changed in that commit**. Make clear whether the change was to documentation or to a device: a documentation edit is not evidence that an installation, repair or migration happened. Do not duplicate a running changelog in the topic documents or commit body.

Read the device README and relevant existing topics before proposing edits. Compare the new evidence with the dated baseline; do not silently discard uncertain or contradictory observations. Offer a precise diff and seek explicit approval **for every GitHub mutation** under the normal workflow. Do not change live device configuration as part of documentation maintenance.

Never commit passwords, tokens, private keys, private proxy credentials or raw sensitive configurations. Omit unneeded public connection addresses and other sensitive infrastructure details. If an existing repository uses a different layout, respect it and propose migration separately rather than restructuring automatically.

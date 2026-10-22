# Workstation documentation

Use this reference when creating or maintaining a workstation record in the user's **already selected or verified bound repository**. This is a documentation convention, not a device scanner or permission to execute commands on a workstation.

## Layout

Use a stable, unique, lowercase device ID (letters, digits and hyphens) rather than an operating-system name. A workstation record has this conventional layout:

```text
devices/workstations/<device-id>/
├── README.md
├── containers/         # optional: deployments hosted on this workstation
│   └── <deployment-id>/README.md
├── system/
│   ├── hardware.md
│   ├── os.md
│   └── security.md
└── environment/
    ├── shell.md
    ├── package-managers.md
    ├── languages.md
    ├── tools.md
    └── network.md
```

The README identifies the physical device, its responsibilities, a short overview, and links to available topic files. Place technical facts in the relevant topic rather than duplicating them in the README. For new registrations, initialize applicable topics with explicit `待审计` fields from the audit catalog below; omit topics confirmed not applicable. Do not create empty, fieldless files. Split a complex topic into extra files only when warranted.

- `containers/`: optional records of container deployments **actually hosted on this workstation**, each under `<deployment-id>/README.md`. List its runtime, image, mounts/network bindings (without secrets), observed state and owning Service link where appropriate. A remote container-management client does not make a remote container local: record that client in `environment/tools.md` and point to the actual host or Service when known. Do not create deployment files solely because a container runtime is installed.
- `system/hardware.md`: model, CPU, memory, storage, GPU and relevant hardware.
- `system/os.md`: operating system, version, build and architecture.
- `system/security.md`: system protection and effective security state: disk encryption, built-in protection features, application firewall status versus saved policy, remote-access services, startup/background items and backup target status as relevant. Never request recovery keys or secrets.
- `environment/shell.md`: shell, terminal and relevant non-secret environment behavior.
- `environment/package-managers.md`: installed package managers and their observed state.
- `environment/languages.md`: runtimes, compilers, SDKs and build toolchains.
- `environment/tools.md`: development applications and supporting tools.
- `environment/network.md`: network clients, proxies, VPN, SSH and remote access, with sensitive details omitted.

This layout works for macOS, Windows and Linux; platform-specific information belongs within the corresponding topic. Do not require an `operations.md` or changelog.

For evidence grading, state-versus-configuration verification, contradiction handling, user-directed audit slimming, cleanup acceptance and audit closure, read [Evidence-first audit practices](audit-lessons.md). These practices apply to all workstation maintenance flows; they do not supply device-specific facts.

## Initial audit coverage and field catalog

For **new workstation registration**, create the applicable topic files with comprehensive candidate fields initially marked `待审计` (Pending audit). The checklist below derives from the existing Mac and Windows infrastructure records; it is a set of questions to verify, **not** a claim that any component exists on the new workstation.

| Topic | Candidate fields to audit |
| --- | --- |
| `system/hardware.md` | Manufacturer, device model and model identifier; processor/SoC model, architecture, logical and physical core counts, performance/efficiency core counts where applicable; GPU model, GPU core count or video memory when relevant; RAM capacity/type; storage device model, medium, interface/protocol, total capacity and per-volume details as relevant. |
| `system/os.md` | OS product/distribution, edition/release, version, build, kernel, architecture; computer/display name and hostname (redact if needed); update or pending-restart status where applicable. |
| `system/security.md` | Read-only inventory of existing OS protections (such as macOS disk encryption, integrity protection and application verification; Windows disk encryption and built-in malware protection; Linux equivalents); distinguish effective firewall state from saved settings; record remote-sharing exposure, already registered login/background components and backup status. Do not create, activate, modify or disable startup tasks or security controls during an audit. Never retrieve recovery keys, credentials or private configurations. |
| `environment/shell.md` | Current and default shells, versions and executable locations; terminal; profile/initialization files and whether present/loaded; PATH resolution and order; aliases, framework/theme/plugins; execution-policy state where applicable; only the presence/absence of proxy variables, never secret values. |
| `environment/package-managers.md` | Each applicable package and version manager, its executable path, version, installation prefix or managed directories; installed package inventories and versions, explicit/top-level packages where supported; installed runtimes, selected/default version and configuration source; manager health checks and unverified capabilities. |
| `environment/languages.md` | Per language: runtimes/interpreters, compilers, version and architecture, installation source, executable path, default PATH resolution and alternatives, associated package managers; SDKs, build tools and targets; verified startup, imports, compile/link/run, build/test capability as applicable. Candidate families informed by existing records include Python, Node.js/JavaScript, Rust, C/C++, Swift, Java and TeX/LaTeX; include only relevant families after applicability review. |
| `environment/tools.md` | IDEs and editors, version/build, installation location, notable bundled build tools; Git/version control; relevant developer utilities, command accessibility and functionality, project run/build verification where provided. |
| `environment/network.md` | Network client and proxy software names/versions, non-secret modes and status at observation time; system/WinHTTP and shell proxy summaries; VPN/TUN categories, DNS and routing summaries; SSH client/version, host-alias summaries and authentication test results; remote desktop methods and tested connectivity; unresolved network checks. Exclude secrets, raw configurations and unnecessary addresses. |
| `containers/` (conditional) | Distinguish a local container runtime, locally hosted deployments, and remote-container management. If local deployments are confirmed, identify their runtime, deployment ID, image/version, service owner, storage and network relationships, and observed health without credentials. Otherwise omit the directory; note installed clients/runtimes in the relevant environment topic. |

## Field coverage refinement from existing records

This refinement combines the already defined field catalog above with the older Mac/Windows records in `NingAloha/infrastructure` and the completed `mba-m4-01` Sandbox audit (2026-10-22). **Additive only:** retain every existing candidate field above and use the following grouped details to avoid omissions. Observed device-specific products, versions and configurations are examples of applicability, never required facts for another workstation.

**Coverage priority:** **Core** means the basic question should be represented at registration (answer with evidence or `待审计`); **Conditional** means establish applicability first and omit confirmed non-applicable sections; **Deep** means collect only for a specific task, contradictory evidence, a security-relevant decision or user interest. A core *question* is not a demand to finish a check on the first session. The user's explicit scope and low-value-check pruning take precedence.

### `README.md` — identity and navigation

- **Core:** stable physical device ID; workstation type/model in non-sensitive terms; primary role, OS family; dated coverage summary; links to actual topic files; source/last-observed date and distinction from live state.
- **Conditional:** linked Services; relationships to other Devices (remote administration, development/testing access); locally hosted container deployments; user-stated Desired goals and important current Pending work.
- **Deep:** lifecycle (replacement/retirement vs incremental change), documentation provenance and contradictory cross-topic status. Do not duplicate technical facts or historic operations here.

### `system/hardware.md` — hardware and peripherals

- **Core:** vendor/model/model ID, SoC/CPU name and architecture, physical/logical cores where exposed, memory size, GPU identity, primary physical disks with capacity/type, volume/filesystem and free-space snapshot.
- **Conditional:** CPU performance/efficiency split; GPU core/VRAM and integrated/discrete/virtual adapters; graphics-driver version and actual driver association; display count and external displays; Thunderbolt/USB or other relevant attached peripherals; battery health where it changes a decision and is safe to collect; device class-specific components.
- **Deep:** disk interface/protocol, partition/volume topology and health, physical-versus-logical units, GPU driver operational status, historical capacity trends. Do not collect unique serials, hardware UUIDs or unnecessary identifying peripheral data.

### `system/os.md` — software platform

- **Core:** product, distribution/edition, release/version, build/kernel, architecture, observed boot or uptime data when relevant, sanitized device naming, evidence dates and confidence level.
- **Conditional:** update availability, pending reboot, update/install history, developer command-line tools provided by the OS, version or edition discrepancies across different read paths.
- **Deep:** correlate OS version, build identifier, kernel and installer/SDK versions only where the discrepancy matters; do not invent explanations, assume a reported update means it completed, or turn unknown reboot status into a definite yes/no.

### `system/security.md` — protection, access and continuity

- **Core:** disk encryption state, baseline platform protection state, **effective** OS application firewall enablement, remote-login/sharing exposure, and whether a system-level backup destination is evidenced.
- **Conditional:** existing OS-specific protection statuses (macOS FileVault, SIP and Gatekeeper; Windows BitLocker and Defender; Linux equivalents), firewall policy versus observed active state, and a read-only list of existing login items, background services, scheduled tasks, system extensions and related drivers where applicable. Listing an item is not permission to install, register, enable, disable or edit it.
- **Deep:** per-app firewall exceptions, packet-filter/network security policy, startup-job target existence, backup/restore verification, remote access attack surface. Prefer read-only checks; do not demand privileged enumeration or harvest FileVault/BitLocker recovery keys, authentication secrets, signing/private keys, certificate stores or full security configurations.

### `environment/shell.md` — user execution context

- **Core:** current interactive versus default/login shell, exact versions and command resolution, terminal(s), basic PATH ordering, user-scoped startup/profile-file presence, observed evidence date.
- **Conditional:** ZDOTDIR/profile loading order, PowerShell version and execution policy **with scope**, aliases/functions versus executable files, shell frameworks/theme/plugins and their versions, configuration initialization for package/runtime managers, system PATH injection sources, per-terminal differences and proxy-variable *presence* (not values).
- **Deep:** repeated/missing PATH elements, initialization origin tracing, command precedence, startup effectiveness, plugin behavior and environment-specific reproductions. A command resolving to its bare name can be a shell function: do not assert an absolute binary path without verification.

### `environment/package-managers.md` — inventories and tooling ownership

- **Core:** applicable manager name, version, resolved executable or function state, installation prefix/managed root, main package inventories with source and timestamp, explicitly installed versus transitive packages where supported.
- **Conditional:** Homebrew formula/cask/leaves/taps and health; Windows Chocolatey/winget or other available managers; npm global packages and registry connectivity without recording private URLs; mise/pyenv/rustup version selectors, sources, active tools/targets; pip/uv/gem/bundler/Cargo inventories as applicable; optional runtime manager state.
- **Deep:** outdated counts as volatile snapshots, manager health warnings, package command failures and previous install attempts with their dates, dependencies and ownership reconciliation, default directories versus alternate installations, known stale links. An earlier failed install is not proof that the current toolchain is broken; a missing PATH command is not global absence.

### `environment/languages.md` — interpreter and build capability

- **Core:** relevant language family and runtime/compiler identity; version, architecture/target, provenance, command path and actual process executable when different; SDK/build-tool association; separate installation detection from a minimal real capability check.
- **Conditional:** Python alternatives/virtual environments/standard-library and package-import health; Node/npm/npx and version-manager association; Rust toolchain/channel/target/rustfmt/Clippy; C/C++ Apple Clang or MSVC/GCC toolset, SDK and linker; Swift toolchain; Java/JDK system discovery and alternate install roots; TeX distribution; platform-specific IDE-bundled compilers.
- **Deep:** clean compilation/link/run of a representative minimal project, IDE-selected interpreter/toolchain, CMake/Ninja/build targets, partial or malformed installations (`sys.prefix`, missing standard library, missing DLLs), conflicting version and SDK values. State **which** test passed; `--version` alone is not project acceptance.

### `environment/tools.md` — applications and developer workflows

- **Core:** relevant IDE/editor identities, observed versions/builds and install source/location; Git client identity/version; key CLI utilities used by the workstation and observed availability.
- **Conditional:** bundled IDE toolchains and executables versus globally available ones; Git editor/config resolution, GitHub CLI and Git LFS; terminal editors/session tools; formatters, search, JSON, document conversion, local database and diagnostics tools; installed GUI apps with no CLI entry; application helper links.
- **Deep:** smoke/clean builds in representative IDE projects, launch and dependency failures, command-line integration, stale symlinks left by removed apps, tool-specific exit code meaning. Distinguish a usable IDE bundle from a working CLI PATH command; record historical checks with their original dates.

### `environment/network.md` — clients, reachability and trust boundaries

- **Core:** network interface categories and **snapshot** connectivity; client-side SSH presence/version, relevant non-secret remote-management roles, proxy/VPN client identity and status; relevant system proxy settings; dated reachability samples if supplied.
- **Conditional:** WinHTTP vs per-user OS proxy vs shell variables; Surge/sing-box and VPN/TUN modes, DNS/routing summaries, active endpoint categories; proxy rule/policy group structure with names/addresses omitted; SSH config/agent/key *presence* and host-block counts; remote desktop client and tested path; inbound SSH only if workstation is acting as a server.
- **Deep:** independently verify configured mode versus actual interface/routing traffic, individual connection path only where safe/needed, split routes and DNS behavior, per-client authentication test semantics (including nonzero success conventions), direct versus proxied reachability, historical/abandoned remote-access paths and cleanup status. Avoid collecting proxy credentials, private hostnames, raw DNS records, IPs, SSH public-key fingerprints or real destination URLs unless clearly needed and approved; redact them before documentation. A connected VPN entry alone does not prove any particular connection traverses it.

### `containers/<deployment-id>/README.md` — conditional host-scoped deployment

- **Core once applicable:** confirmed local host/device ID, deployment ID and runtime, image/tag or digest at observation time, owning Service link, observed lifecycle/health and evidence date.
- **Conditional:** compose/project association, container ports and host-published bindings, mounts/volumes and persistent-data ownership, network membership, startup/restart behavior, resource limits, dependencies and health-check meaning (sanitized).
- **Deep:** application-level acceptance independent of container health, update/rollback consequences, cross-service dependencies and host resource impact. A remote GUI/CLI manager does not place its remotely managed containers under this workstation. A runtime installed without deployments does not require this directory.

### Consistency and audit finish

Before closing a registration or maintenance session, check that the README links only real files and accurately summarizes coverage, that versions and runtime ownership agree across `languages.md`, `package-managers.md` and `tools.md`, and that client, network and Service links use the same documented identities. When later evidence corrects a stale README claim (for example, cleanup of container-related dangling symlinks), propose a scoped synchronization rather than reopening an entire device audit.

For each candidate field, initially write a meaningful `待审计` value, with no fabricated date or supporting evidence. Prefer a concise table per topic with columns such as `Parameter | Value | Evidence / checked at`. A `待审计` entry is an outstanding audit question, **not** a measured fact, a Desired goal or proof that a component is missing. For conditional items, first ask the user whether the capability or component applies.

During each documentation-maintenance session for a device, scan the **repository documentation** for `待审计` fields and offer a small, prioritized batch of user-run checks. This is not a direct OS scan. Do not hijack a focused task: briefly summarize outstanding coverage and let the user defer it. When the user returns evidence, update the field with the observed value, source, date and validation level; when confirmed not applicable or not installed, record that distinction and propose removal of irrelevant placeholders. Never delete a field merely because a command produced no output or the user skipped a check. Every document deletion or update follows the shared conversation-scoped GitHub authorization policy; deletions and scope expansions require separate approval.

Once a field has been resolved, do not retain redundant placeholders indefinitely. Keep real unresolved issues in Pending and user-stated goals in Desired. Git records what the documentation edit actually changed. This catalog covers workstations only and does not define a server/container internal schema.

## What a document says

Documents describe only **Facts**, **Pending**, and **Desired**:

- **Facts**: what is known, including its evidence source, observation or verification date, and relevant uncertainty. Distinguish a detected installation, an actual functional test, and a user report. Never present a historical baseline as live monitoring.
- **Pending**: unfinished work or unresolved questions, without implying they were completed.
- **Desired**: intended configuration or outcomes, clearly separate from observed facts.

These are semantic categories, not mandatory headings. Omit empty sections; use natural headings when clearer. Keep current unresolved issues in the appropriate topic, not in an accumulated operations diary.

## User-mediated workstation interaction (v0.1)

**The agent does not operate or inspect a workstation directly.** This remains true even if the host exposes terminal, local files, SSH, remote execution, automation, or other operating-system tools. Such tools must not be used for workstation inventory or diagnosis in this version. GitHub tools are for reading and, after an explicit, sufficiently scoped conversational authorization, updating the documentation repository only. The user runs commands, navigates GUI screens, and decides what results to share.

### First registration

When the user asks to register a new workstation:

1. Resolve the already selected or verified bound documentation repository. Read its root inventory and existing workstation IDs; never guess another repository. Do not restart the GitHub setup wizard for a normal registration request.
2. Establish whether this is a new physical device or an existing device evolving over time; obtain or propose a unique stable device ID and let the user confirm it. Ask for the operating-system family only if it is not already clear. Do not assume the agent host is the device being registered.
3. Use the layout above as a **coverage checklist**, not a questionnaire that must all be completed at once. Identify what evidence is missing, including relevant container relationships when applicable, and give the user small, manageable batches of read-only instructions, appropriate to their OS. Include the purpose of each command or GUI step, what to copy back, and any privacy-sensitive fields to omit. Prefer straightforward built-in OS tools; do not ask the user to install diagnostic dependencies merely to fill a document.
4. The user runs the instructions themselves and shares selected terminal output, screenshots, or descriptions. Interpret only that supplied evidence. Record its source and date and distinguish user reports, detected components and demonstrated working behavior. Never claim to have executed a check.
5. Populate supported Facts; put unresolved or deferred checks in Pending. Ask the user for Desired goals instead of inventing them. An incomplete audit is acceptable: keep applicable fields marked `待审计`, summarize coverage and the next useful, optional batch rather than blocking registration.
6. Present the proposed device tree and the complete creation/update diff, along with uncertainty and privacy review. Use the shared conversation-scoped authorization workflow: if registration was already explicitly approved for these paths and proposed contents, do not ask again; otherwise seek one bounded approval. After an authorized write, verify the resulting commit and files; otherwise stop with the proposal.

### Routine audit of an existing workstation

Trigger: the user asks to audit/check a device, continue outstanding verification, or review documentation quality. This is **not** a new registration.

1. Resolve the bound repository and device ID; read the device README and relevant topic documents. Scan for `待审计` and `未取证`, stale dated facts, cross-file inconsistencies and prior unresolved questions. Do **not** treat all dated facts as automatically invalid.
2. Prioritize based on the user's request, materiality, risk and age of evidence. For a broad audit offer small topic-sized batches; for a focused request inspect only the necessary topics. Report the existing baseline separately from what has been checked today.
3. Give the user safe, read-only OS-specific commands or GUI steps, including what outputs to share and what to redact. **Never execute device commands yourself**, even if the agent host is the same device. Avoid routine network-reaching checks such as `brew outdated`, and never presume CLI discovery covers every possible installation path.
4. Compare user-returned evidence with the baseline field by field. Distinguish command discoverability, installation evidence, version output and functional verification. For shell aliases/functions, `command -v` may return a name rather than an absolute executable path; use an appropriate user-run disambiguation step before claiming a path.
5. Preserve supported facts, update verified values and observation dates, leave unexplained changes Pending, and remove non-applicable placeholders only after appropriate evidence and authorization. **Calibrate absence claims to the search scope:** a command missing from PATH is `not resolved in this shell`, not `not installed`; a standard manager reporting no runtime does not exclude nonstandard locations; an empty Cargo install list or default bin directory does not exclude alternate `CARGO_HOME`/installation roots. Name the commands, locations and limits rather than claiming global absence. User-directed pruning may retire low-value questions without treating them as solved. Do not quietly replace contradictory evidence with a guess.
6. Present a compact audit result: newly verified, changed, unchanged, unresolved, and proposed documentation edits. Apply only user-authorized GitHub edits under the shared workflow. An audit need not produce a commit.

### Maintenance after a reported device change

Trigger: the user says a package was installed/updated/uninstalled, a setting was changed, a component was replaced, or some infrastructure state changed.

1. Read the documented baseline and the affected topic(s), plus directly related device or cross-device records if the change affects them. Do not restart registration or re-collect the whole inventory.
2. Treat the report as a user report until the user supplies suitable supporting evidence. Offer the smallest relevant user-run verification, including functionality or connectivity where necessary.
3. Compare before/after values. Record **observed current state** and evidence date, not an invented change date; if execution time is only user-reported, say so. Preserve meaningful gaps and unexpected side effects as Pending.
4. Update linked records consistently (for example, runtime version in both language and package-manager records), and avoid unrelated formatting or cleanup.
5. Confirm documentation write scope in the conversation once; if the user's explicit request already authorizes the bounded change, do not ask again merely because a diff was prepared. Commit and verify with detailed history, or leave a proposed diff when authorization or evidence is insufficient.

### User-requested solution, guided execution and acceptance

Trigger: the user describes a goal such as setting up a toolchain, resolving a conflict, improving a workstation workflow, or configuring a new service/client.

1. **Understand the outcome** and material constraints without re-asking facts already in the repository. Read the device baseline, relevant software/network records, resource limits and dependencies. For inter-device changes read both sides; for domains/ingress read shared routing records.
2. **Recommend a concrete plan** that reuses current infrastructure, compares meaningful alternatives only when relevant, names expected results, compatibility and conflicts, risks, prerequisites and rollback for potentially disruptive steps. Distinguish proposal/Desired from existing Facts.
3. **Guide, do not operate:** offer small ordered commands or GUI instructions for **the user** to execute. Unlike audit commands, these may intentionally install software or change settings, but label every mutating command and its consequences clearly; obtain the user's explicit decision to proceed with risky device changes. Do not use host tools, shell, SSH or remote execution to perform workstation/device mutations.
4. **Interpret user-returned results** after each stage. A zero exit code or a command being issued is not sufficient proof of the intended outcome. Request appropriate independent functional verification and verify no material collateral failure where feasible.
5. **Document acceptance:** when successful, update the actual observed Facts, evidence and validation scope, close supported Pending entries, and reconcile Desired. On partial success or failure, record only observed state and remaining Pending; do not mark the intended state completed or invent an installation.
6. **Commit authorized documentation changes** via the shared GitHub workflow. User authorization to perform a device operation is distinct from authorization to change the GitHub repository. A user's request to **record** the verified result can authorize the bounded documentation change without redundant approval.

For all three maintenance modes: keep a device-maintenance task scoped to the selected repository and paths, summarize unresolved audit candidates without hijacking a focused request, and do not use repository documentation as a substitute for a live measurement.

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

Read the device README and relevant existing topics before proposing edits. Compare the new evidence with the dated baseline; do not silently discard uncertain or contradictory observations. Offer a precise diff or change summary and follow the shared GitHub authorization workflow; do not repeat an approval request when the conversation already explicitly authorized that exact bounded change. Do not change live device configuration as part of documentation maintenance.

Never commit passwords, tokens, private keys, private proxy credentials or raw sensitive configurations. Omit unneeded public connection addresses and other sensitive infrastructure details. Use the canonical `devices/workstations/<device-id>/` path for new registrations. Do not create compatibility aliases or automatically migrate existing paths; any restructuring requires separate explicit approval.

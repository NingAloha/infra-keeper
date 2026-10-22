# Infrastructure repository layout

Use this layout for a newly initialized InfraKeeper documentation repository. The repository is a Git-backed record of Facts, Pending work and Desired states, **not** a monitoring system or an execution workspace.

```text
README.md
devices/
  workstations/
    <device-id>/
      README.md
      containers.md
      system/
        hardware.md
        os.md
      environment/
        shell.md
        package-managers.md
        languages.md
        tools.md
        network.md
  servers/
    <device-id>/
      README.md
      ... server-specific topics (defined separately)
containers/
  <container-id>/
    README.md
domains/
  routing.md
```

## Responsibilities

- Root `README.md`: the global entry point, inventory of active devices with stable IDs, their responsibilities and links to device READMEs; links to cross-device relationships. Keep detailed device configuration out of the root index.
- `devices/workstations/<device-id>/`: personal computers and developer workstations regardless of operating system. Follow [workstation documentation](workstation.md). The agent guides users in collecting evidence; users operate their own devices.
- `devices/servers/<device-id>/`: machines whose primary role is providing services. Each has an entry README. The server's detailed topic layout and collection interaction are not yet specified; do not invent a standardized server schema from the workstation template.
- `containers/<container-id>/`: global records for containers, independently of their host device. Record container facts, pending work, desired state and links to related devices without duplicating device records. A container may run on a workstation or server; its directory does not follow the host. A detailed container schema is not defined yet.
- `devices/workstations/<device-id>/containers.md`: an optional index and short description of containers related to this workstation, including links to their records under `containers/` and the relationship (hosted locally, managed remotely, etc.). It is not a duplicate container configuration file.
- `domains/routing.md`: domain, DNS, external entry-point and routing relationships spanning devices. Keep shared relationships here rather than duplicating contradictory versions across device records.

Directory names `devices`, `workstations`, `servers`, `containers` and `domains` are literal and spelled out, not abbreviated. Device IDs are stable, lowercase, hyphen-separated identifiers and unique within their category. Categorize by primary role, **not** operating system. A Linux desktop belongs in `workstations`; a service host belongs in `servers`.

## Working with the repository

After the user selects or verifies a repository binding, start at its root README and follow the relevant links; do not enumerate unrelated repositories. New registration updates the corresponding device subtree and root index as one proposed scope, subject to one explicit task-scoped conversational authorization for the proposed changes. Do not create empty topic files merely to match the diagram.

Documents hold dated facts and evidence, outstanding work, and user-defined intended states. Git commits describe the actual documentation changes made, not an invented history of device operations. Never treat repository text as proof of live device health. Never store credentials, keys or sensitive connection details.

This v0.1 structure is normative for new InfraKeeper records: do not add old-path compatibility rules or automatic layout migration. Never reorganize existing data or rename paths without a separately reviewed and approved change.

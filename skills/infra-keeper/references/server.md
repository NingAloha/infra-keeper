# Server documentation and audit

Use for registering and maintaining a server in the user's selected/bound infrastructure documentation repository. This reference is based on **the documented audits**, not current runtime verification, of server-02 and server-03 in `NingAloha/infrastructure` (October 2026). Values, provider names, service names, dates, paths and ports from those servers are **examples of evidence** and must never be copied as facts about a new server.

## Layout and ownership

```text
devices/servers/<device-id>/
├── README.md
├── system/
│   ├── hardware.md
│   ├── os.md
│   ├── resources.md
│   └── security.md
├── environment/
│   ├── packages.md
│   └── runtimes.md
├── network/
│   ├── interfaces.md
│   ├── firewall.md
│   └── connectivity.md
└── containers/                  # conditional: only locally hosted deployments
    └── <deployment-id>/
        └── README.md

services/<service-id>/
├── README.md
├── deployment.md                # optional: actual device/container relationships
├── access.md                    # optional: service-owned domain, DNS, TLS and ingress
└── operations.md                # optional: business data/backup/restore/acceptance
```

The directories are **topic boundaries, not an obligation to create every file**. Keep initial fields `待审计` only for relevant unresolved questions; omit confirmed inapplicable topics and never create empty files. Keep host and Service records cross-linked but don't duplicate a fact across both.

**Device** owns host CPU/memory/disk, OS, user/privilege/service-manager state, local package/container runtime, host listeners, host firewall, cloud instance/network policy references and host-level snapshots. **Host-scoped Container** owns deployment ID, actual host, image, bind/port/volume state, resource limits and observed container health. **Service** owns business purpose, cross-device dependencies, deployment relations, client-facing domain/DNS/TLS/routing, authorization boundary, end-to-end acceptance, data ownership and application-level backup/restore. A direct-IP service does not need a domain. A systemd service without a container is a valid deployment; do not invent container records.

The host-level security, network and resource fields must work for VPS, VM, bare-metal and managed platforms. Provider-specific details are conditional, not universal. `operations.md` is reserved for **Service recovery requirements**, not a redundant device event diary; device outage chronology and corrective actions live in detailed Git commit history and, if still important to operations, a concise dated fact/limitation in the relevant topic.

## Layered field catalog

**Core**: represent the question in the initial audit and record supported values or `待审计`; don't require every check before registration. **Conditional**: first establish applicability. **Deep**: check when risk, troubleshooting, a discrepancy or the user's goal warrants it. An incomplete audit is acceptable.

### `README.md`: identity and index

- **Core:** stable server ID, role, environment (production/test), hosting category and provider when known, evidence-as-of date, existing topic links, linked Services and at-a-glance audit coverage.
- **Conditional:** associated devices/admin clients, host-owned container deployments, support/maintenance responsibilities, expected availability and user Desired goals.
- **Deep:** lifecycle state, replacement versus rename, retiring instances, dependency map, known material limitations. Do not restate runtime versions, credentials or raw endpoints from other topic files.

### `system/hardware.md`: allocated hardware and instance characteristics

- **Core:** physical/VM/cloud type, architecture, effective CPU/vCPU and model where exposed, memory size, storage devices/allocated capacity.
- **Conditional:** cloud region/zone, instance class and plan, physical versus virtual resources, disk protocol/medium, provider quota/CPU credit/bandwidth limits, network device capability. Label provider advertised RAM/disk **separately** from guest-reported usable values; they need not match.
- **Deep:** hypervisor limits, attached storage volumes and persistent identity, resource resize boundaries and cost-related inventory if supplied (not speculative).

### `system/os.md`: OS and boot state

- **Core:** distribution/version, kernel/build, architecture, host identity redacted as appropriate, read-only SSH/console evidence date, boot/uptime status when provided.
- **Conditional:** image source, installation/update history, security patches/pending reboot, installed kernel versus active kernel, time synchronization/timezone, systemd/init version, package update state.
- **Deep:** boot histories, reboot sequence and shutdown anomalies, package-version anomalies, reboot-after-upgrade acceptance; distinguish login banner from independently queried facts.

### `system/resources.md`: host capacity and pressure

- **Core:** total/available RAM as snapshot, swap present/size/used, disk used/free and filesystem, CPU usage/load at observation time, relevant uptime.
- **Conditional:** memory allocation by service/container, OOM evidence, swap configuration and persistence, filesystem mounts/inodes, high-usage paths, processes using memory/CPU, provider metrics where user supplies them.
- **Deep:** time-series trends, memory pressure/latency correlation, cloud platform incidents, root cause of outages, sizing/scale recommendations. A single swap value or cloud package size cannot prove OOM or a memory leak. Do not run intrusive benchmarks or broad filesystem scans in production.

### `system/security.md`: server access and host protections

- **Core:** SSH server enabled/listening state, authentication/privilege policy **summaries without credential material**, user privilege categories, updates, host security control state, backup/recovery prerequisites.
- **Conditional:** SSH password/root-login policy, sudo boundaries, credential/secret storage ownership, systemd service identities, file/directory permissions of sensitive config (metadata only), auditing/journal retention, security update policy.
- **Deep:** systemd unit hardening, sensitive path ownership drift, targeted access-control tests, intrusion/incident triage. Do not print `/etc/shadow`, SSH keys, service env, authorization tokens, TLS private keys or complete private config. Lack of permission to read a protected path **does not prove the file is absent**.

### `environment/packages.md`: OS package and update provenance

- **Core:** OS package manager identity, system packages necessary to operate documented services, installation source and observed versions where relevant.
- **Conditional:** apt/dpkg, snap, custom scripts/vendor installers or other OS-specific managers; installed versus available updates; package pinning/hold; update channel and rollback mechanism.
- **Deep:** update failure history, security advisories and compatibility, dependency drift, package/service binary provenance. Do not run updates or upgrades as part of a read-only audit.

### `environment/runtimes.md`: host execution layer

- **Core:** init/service manager, relevant active/enabled systemd units, host container runtime if installed, versions/path and basic status.
- **Conditional:** Docker/Compose/Podman/containerd versions, Compose project or unit association, proxy/reverse-proxy runtime, native binaries, runtime execution users, configuration file **paths and permissions**, start/stop/restart and logging methods.
- **Deep:** effective unit state versus config-on-disk, changed unit files requiring reload, orphaned runtime processes, clean restart acceptance and rollback, container runtime dependency/health; do not equate an `active` unit with working application behavior.

### `network/interfaces.md`: host-level network

- **Core:** IPv4/IPv6 capabilities and observed interface/route categories, private/public role without posting raw IPs, listeners with protocol/address scope (loopback versus public).
- **Conditional:** fixed or ephemeral IP assignment, IPv6 address availability, default routes, DNS resolver, tunnel/VPN interface presence, local bindings for reverse proxies/containers, network namespace relationships.
- **Deep:** route source verification, asymmetric paths, dual-stack differences and post-migration address updates; avoid unnecessary address disclosure.

### `network/firewall.md`: layered exposure

- **Core:** relevant listeners, host firewall engine and **effective** enabled/default state when checked, cloud/provider ingress rules when applicable, IPv4/IPv6 and TCP/UDP comparison.
- **Conditional:** UFW/nftables/iptables, cloud control plane ingress/egress, security groups, reverse proxy upstream isolation and localhost-only published ports; configuration precedence and propagation.
- **Deep:** end-to-end reachability from authorized paths, unexpected exposed ports, mismatch of listeners versus provider ACLs, source allowlists, trusted proxy identity. `ufw` not found does not imply no firewall; a listening port does not imply cloud ingress is open; a single `403` or `404` is not a full security proof. Do not change firewall or remote access policy during an audit.

### `network/connectivity.md`: host transport and verification evidence

- **Core:** administrative connectivity via user-reported SSH or provider console, tested transport paths with timestamp/scope, relevant external dependency links.
- **Conditional:** ICMP/TCP/UDP checks, client-side v4/v6 tests, authorized direct/proxied paths, latency/throughput samples, DNS/CDN fronting as a cross-reference to Service access, proxy/TUN behavior as it affects observed paths.
- **Deep:** independent validation of ingress chain, provider ACL versus OS policy versus reverse proxy versus application, client path/policy conflict, sustained reliability. A successful client test proves **that test path at that time**, not all clients or continuous uptime.

### `containers/<deployment-id>/README.md`: only if hosted locally

- **Core once applicable:** actual host and deployment ID, runtime, image/tag or digest and observation date, container running/healthy state, owning Service, relevant Compose/project association.
- **Conditional:** published/bound ports (loopback/public distinction), internal container networking, dependencies, persistent mounts/volumes, restart policy, resource constraints, health-check definition and observed status.
- **Deep:** rolling or manual upgrade procedure, recovery of persistent storage, application verification independent of health, mapping changes after host migration. A container being `healthy` never substitutes for a service's API/client tests.

## Per-file recording contracts

The Core/Conditional/Deep catalog above determines **which questions** are worth asking. The contracts below determine **how answers are stored**, which file owns each answer, and the minimum evidence required. They add to—not replace—the existing field catalog.

For each factual row prefer `Item | Observed value | Evidence and observed at | Verification boundary`. Record timezone or UTC for time-sensitive events. Use `待审计` only for applicable, unresolved questions; `未取证` for a specific important claim not yet supported; `不适用` only when applicability was established. Do not output raw config/secret data. A future Desired setting must never appear as a current fact.

| Document | Suggested internal sections | Ownership and minimum validation |
| --- | --- | --- |
| `README.md` | Identity and role; device/topic index; linked services and host deployments; coverage and material unresolved risks | Identifiers and links only. All links must resolve; don't repeat version, endpoint and health details from topics. |
| `system/hardware.md` | Provider/instance identity (redacted); allocation and observed hardware; attached storage; evidence limits | Separate provider advertised vCPU/RAM/disk from guest-reported hardware and capacities. Console screenshot is not guest-level verification. |
| `system/os.md` | Distribution/kernel; host boot and clock; updates/reboot requirement; evidence timeline | Banner, package inventory, `uname`, boot history and update command are separate observations; infer neither current kernel nor successful reboot from package installation alone. |
| `system/resources.md` | CPU/load; memory/swap; disks/filesystems; resource consumers; trends and limitations | Each measurement includes sample time and units; use snapshot or multi-sample qualifier. Avoid concluding memory leak/OOM from swap alone. |
| `system/security.md` | Administrative access; effective controls; service identities and secret-path permissions; host audit/update policy; limits | SSH listener, login authentication, service accounts and protected file metadata are distinct facts. No secrets or gratuitous privilege escalation. |
| `environment/packages.md` | Package managers; installed components/versions; update and pinning status; install provenance; package failures | Installed, selected, available and functioning are separate states. Historic install errors stay dated, not extrapolated to present. |
| `environment/runtimes.md` | systemd/init; containers and compose runtime; native runtimes/reverse proxies; unit/config metadata; operator procedures | Distinguish unit enabled, active, loaded version, listening socket, clean start and tested operation. Runtime installed does not prove hosted containers. |
| `network/interfaces.md` | Interfaces; v4/v6 roles; routing/resolvers; local listeners and bind scopes | Preserve protocol + port + bind address category (loopback, private, wildcard) with date. Do not confuse listener with external reachability. |
| `network/firewall.md` | Host firewall engine/state; IPv4/IPv6 effective policy; provider ingress/egress; cross-layer exposure mismatches | Explicitly compare host listener, host policy, provider rule, external path. Report unknowns; absence of UFW does not imply absence of firewall. |
| `network/connectivity.md` | Management access; host outbound checks; reachable transport samples; cross-device observed paths; reachability limits | Name vantage point, protocol and tested action; a single remote success doesn't prove all routes or uptime. Service URL/DNS/TLS semantics live in Service access. |
| `containers/<deployment-id>/README.md` | Host and service owner; image/compose; ports/networks; volumes/persistence; lifecycle/health; resources and limitations | Health result must be container-specific; cross-reference business tests and backups in Service. Do not duplicate secret environment data. |

### Topic-specific acceptance examples

- **Hardware and OS:** corroborate guest-reported OS/kernel with read-only commands; distinguish cloud-console plan from memory actually visible to guest. Mark release/kernel changed by update only after actual observation.
- **Resources:** collect a small snapshot of `free`/`df`/load and (when justified) limited process metrics; timestamp each. For outage diagnosis, use a narrow user-returned boot/journal excerpt plus historical comparisons, **not** broad secret-bearing log dumps or assumed OOM.
- **Administrative security:** record SSH service/listener and basic access status without reading private keys or passwords. A permission-denied `test -e` in a protected directory cannot establish missing config; ask for a targeted metadata-only privileged check only when justified.
- **Package/runtime:** identify installed tool binary/version, active systemd unit, configuration path existence/permissions and listener separately. `systemctl active` alone is not a passing API test; a valid config file on disk is not proof the process loaded it.
- **Network:** compare TCP/UDP and IPv4/IPv6 separately across effective host firewall and provider console. If an application listens on UDP 443 but no provider UDP 443 rule is shown, record a possible gap instead of silently considering it reachable.
- **Container:** use inspected container state and health as one layer; only a Service-level test establishes that the actual application endpoint performs the tested behavior.
- **Service admission:** a HTTP 200 on a public API and a HTTP 404 on one admin path prove only those two requests. For allowlisted admin entry, authorized-path 200 and unauthorized-path 403 demonstrate the tested differential but do not establish all bypasses are impossible.
- **Certificate and deployment change:** distinguish former ACME/domain mode from newer direct-IP/private-cert or pinning mode, validate client capability after a change, and leave stale DNS, ports, restarts or certificate rollout Pending until verified.

### Cross-document reconciliation

Check before each logical task is declared complete:

1. README links to every existing server topic and hosted container deployment, and refers to actual linked Services rather than a fabricated global service inventory.
2. `hardware.md` allocated memory/disk and `resources.md` guest-observed memory/disk have consistent units and deliberately different meanings; `os.md` records observed active kernel, not just installed package version.
3. `runtimes.md` installed container engine and `containers/` hosted instances agree. A native systemd business service must link to its independent Service without inventing a container.
4. `interfaces.md` listener protocol/binding, `firewall.md` host/cloud ingress and `connectivity.md` actual test vantage do not claim the same proof level.
5. Host config/runtime facts and Service `deployment.md` agree on which Device actually hosts each component. Domains, DNS, external TLS/route and client-facing URLs appear under Service `access.md`, **not** the server's host-network facts as a duplicate source.
6. Container health, local app health and client/business acceptance are independently evidenced. Database data protection and restoration results live in Service `operations.md`; cloud snapshot status belongs to Device.
7. Check last-minute corrective findings against earlier README summaries and topic descriptions; maintain current facts while preserving history in commits, not by dumping an audit transcript into Markdown.

## Related Service documentation

Create a Service record when the workload has a distinct purpose or lifecycle; do not force every host daemon into a user-facing Service. One host may run several Services; one Service can span devices and instances.

- `services/<service-id>/README.md`: service ID, purpose, responsibilities, dependencies and status/evidence summary; links.
- `deployment.md`: current hosts, container or systemd deployments, relevant software/image versions, upstream and database relationships, deployment/rollback boundaries. Point to device/container source-of-truth for host facts.
- `access.md`: service-owned domain(s) **only if used**, DNS A/AAAA/proxy mode, CDN/WAF/TLS, certificate type/issuer/expiry/renewal or pinning (not secret material), edge/reverse-proxy routing, external and admin access requirements, IP allowlist **semantics** without raw IPs, public/private API exposure and evidence. When a service migrates from domain+ACME to direct IP+self-signed TLS, preserve the change in Git and keep only current entry-point facts in the record; historic DNS is not automatically considered removed without evidence.
- `operations.md`: service-level critical data/persistence, backup approach and verified status, database-consistent export versus ordinary file copies, protected secrets policy, restore procedure/actual drill evidence, application-level and cross-client regression acceptance, update and rollback plan.

## Audit workflows and production safety

1. **Read before anything:** read the bound repository's root README, server README, relevant host topics, linked Service records and cross-device/client evidence. For existing legacy layouts, read their records without treating the proposed new paths as already present.
2. **Select scope:** for registration initialize relevant Core questions and only applicable Conditional topics; for maintenance examine specific changed/unknown facts, not the full machine. Prioritize backup/recovery, public exposure, SSH access and resource risks according to the actual request.
3. **User-mediated read-only evidence:** give short, OS-specific commands or GUI/cloud-console steps to the user; **never invoke host shell, SSH, remote exec or cloud mutating tools to inspect or change a server**. Warn before commands that may reveal IPs, credentials, logs, auth headers or tokens, and have the user redact output. Use bounded logs and metadata checks; do not copy full sensitive configuration.
4. **Evidence levels:** distinguish reported intent, config-on-disk, syntax validation, loaded/effective state, process/listener, container health, local HTTP/API, authorized remote reachability and full client-level behavior. A later observation can correct an earlier inference: preserve observation dates and the correction.
5. **Non-disruptive verification:** avoid CPU/memory stress tests, bulk data reads, unrestricted port scans, production backups/dumps or permission-changing commands as routine audit steps. If elevated read-only inspection is essential, explain why and seek user consent before presenting it; allow skipping it.
6. **Changes and acceptance:** any installation, restart, config edit, cleanup, firewall modification, cloud setting, database operation, credential/certificate rotation or backup/restore test is a **separately decided user-executed device operation**. Analyze dependencies, impact, rollback and expected verification first; user returns the outcome; do not infer success merely because a command ran.
7. **Documentation:** update only evidenced Facts, actual Pending and user Desired. Keep service, host and container links consistent, reconcile dated changes across files, and use detailed Git commit messages. One task-scoped explicit authorization covers bounded document writes; it never authorizes live operations.
8. **Closure:** differentiate resolved, unresolved, not-applicable and user-retired low-value questions. Close the agreed audit when the user says it is complete, with a coverage and limitations summary—not a claim that production is fully secure or continuously healthy.

### Lessons specific to the two server records

- **server-02 example:** memory and swap snapshots on a small instance do **not** establish the cause of a later outage; Compose health, local service HTTP checks and public endpoints demonstrate different levels. Administrative source-IP access must not be weakened in order to make troubleshooting easier. PostgreSQL requires a consistent backup method and actual restore evidence before claiming recoverability.
- **server-03 example:** do not inherit old server-01's packages, firewall openings, ports or service roles. A cloud plan memory figure differs from what Linux reports as available RAM. The historic ACME/domain mode and later direct-IP self-signed/pinned-certificate mode have distinct evidence and cleanup requirements. A successful IPv6 client session does not prove Windows clients were migrated, old DNS deleted, unused port 80 closed or ongoing availability.

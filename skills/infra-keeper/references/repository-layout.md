# Infrastructure repository layout

Use this layout for **new InfraKeeper records**. It describes dated Facts, Pending and Desired, not real-time monitoring. **Device and Service are independent entities; container deployments belong to their host Device; domains and their access configuration belong to their Service.**

```text
README.md
devices/
  workstations/<device-id>/
    README.md
    system/
    environment/
    containers/           # optional, deployments hosted on this workstation
      <deployment-id>/README.md
  servers/<device-id>/
    README.md
    system/                # server topic schema to be designed
    environment/           # optional
    network/               # optional
    containers/            # optional, deployments hosted on this server
      <deployment-id>/README.md
services/
  <service-id>/
    README.md
    access.md              # optional: domain, DNS, TLS, routing and ingress
    deployment.md          # optional: host/container/service relationships
    operations.md          # optional: business backup, restore and acceptance
```

## Ownership and identity

- **Device**: a physical computer or virtual machine with a stable identity, resource limits, host OS, network and runtime configuration. Workstations and servers are categorized by primary role, not OS. Each device README indexes its own applicable topic files.
- **Service**: a durable user-facing or supporting function whose identity does not depend on its current host. Document service purpose, dependencies, lifecycle, acceptance and its currently evidenced deployment. A service can use multiple devices and containers. Keep its README as an index; create topic files only when useful.
- **Container deployment**: a host-scoped instance, not a global standalone entity. Record it under `devices/{workstations|servers}/<device-id>/containers/<deployment-id>/` **only when hosted on that device**. A container runtime may exist without any deployed containers; neither a remote-management client nor a container listed on another server belongs under this host. Treat Podman/Docker/containerd similarly. Shared or orchestrated workloads that cannot honestly be attributed to one fixed host should be modeled through service deployment relationships until their own schema is designed; do not invent a permanent host.
- **Domain and access**: a domain is an attribute/entry point of its owning Service, not a global Domain entity. Put DNS record intent/observation, TLS, CDN/proxy, routes, port mapping, authorization and relevant ingress evidence in `services/<service-id>/access.md` (or the service README for small cases). When multiple services use the same hostname, record each service's owned paths/routes and cross-check them for contradictions. Do **not** create `domains/routing.md` or a global domain registry by default.
- **Root README**: global navigation of Devices and Services with concise roles and links, not a competing source of detailed configuration.

## Fact ownership and links

- Host OS, resources, runtime installation, network interfaces and locally hosted deployment state belong to **Device**.
- Individual container image/version, host association, mount/network bindings and instance health belong to the host's **container deployment**. Sensitive environment variables, tokens, private keys and raw configs must not be stored.
- Business meaning, domain entry points, cross-device dependencies, user-observable behavior, data ownership, business backups and restore acceptance belong to **Service**. Record system snapshots/host backup arrangements under Device where appropriate.
- Cross-link instead of duplicating an authoritative fact. For a host migration, preserve service identity and update its deployment links; the old host's deployment history remains in Git.
- An external DNS/CDN platform or shared proxy may affect several services; document the portion of routing owned by each service and cross-reference shared infrastructure when relevant rather than reintroducing a mandatory independent Domain entity.

## Scope, safety and transitions

- Read the selected or verified bound repository's root index and relevant Device/Service READMEs before changing topic files. For cross-device, network or public ingress work, inspect every affected relationship and the owning Service's access record.
- Existing repositories may have legacy `devices/server-02/`, `containers/` or `domains/routing.md` records. They remain historical/current baselines **until a separately approved migration**. Do not silently delete, move or treat them as absent. The new layout applies to new registrations and future approved migrations; no automatic compatibility aliases or automatic restructuring.
- Do not invent a full server or cluster audit schema from this outline. Design it separately before initial server registration. No empty topic files merely to match a diagram.
- An initial registration or migration uses a bounded GitHub write authorization; destructive moves/deletions/restructuring need separate explicit approval under the GitHub workflow.
- Never infer live runtime health from documentation. Git commits describe documentation changes, not device or service operations. No secrets or unnecessary sensitive topology in files or commit messages.

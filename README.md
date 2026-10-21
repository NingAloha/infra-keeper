# InfraKeeper

InfraKeeper is an open-source Agent Skill for maintaining a documented personal or small-team infrastructure: devices, servers, networks, domains, and deployed services.

It makes an agent read the existing infrastructure record before it advises on an existing system, distinguishes recorded configuration from live facts, and plans changes around conflicts, verification, and rollback.

## What is included

- `SKILL.md` — the installable skill entrypoint.
- `references/` — repository-discovery and safe-maintenance guidance.
- `templates/infrastructure/` — sanitized starting files for a documentation repository.
- `examples/fictional-studio/` — an entirely fictional, non-deployable example.
- `evaluations/cases.json` — behavior scenarios and review rubrics.
- `tests/` — offline checks for fixture safety and evaluation completeness.

## Install

Clone this repository, then install or copy the `infrakeeper/` directory into the skills location used by your agent platform. The skill itself has no runtime dependency and never assumes a particular cloud, operating system, or automation tool.

## Start a documentation repository

Copy the template tree, then replace bracketed fields with non-secret descriptions:

```text
templates/infrastructure/
├── README.md
├── domains/routing.md
└── devices/_device-template/
    ├── README.md
    ├── system.md
    ├── network.md
    ├── operations.md
    └── services/
        ├── README.md
        └── _service-template.md
```

Keep credentials in a secret manager and refer to their owner or rotation procedure, never their value. The template deliberately omits real addresses, provider account identifiers, production hostnames, and executable deployment commands.

## Use

Ask for an inventory, investigation, proposal, or record update in ordinary language. For example:

> Use `$infrakeeper` to assess whether adding a monitoring service to `edge-01` conflicts with the documented network and services.

The skill should inspect the root inventory, the device record, relevant service records, and routing documentation before proposing a plan. It should label the result as documented baseline versus live verification.

## Validate the release

Run with Python 3:

```bash
python3 tests/test_assets.py
```

This performs offline checks only. It does not contact devices, cloud providers, or GitHub.

## Design notes

The repository layout was inspired by a real-world pattern of a top-level inventory, device landing pages, focused system/network/service records, and a separate routing map. This project contains no copied configuration, no Git history, and no real infrastructure details.

## License

MIT. See [LICENSE](LICENSE).

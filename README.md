# InfraKeeper

An open-source Agent Skill for **evidence-first maintenance of infrastructure documentation repositories**.

## Status

**GitHub integration foundation (experimental).** The Skill defines repository discovery, version checks, approvals, and two GitHub backends. It is not yet a complete infrastructure-operations agent and does not configure GitHub credentials on its own.

## Install the Skill

Install or copy this directory as an Agent Skill supported by your agent host, preserving `SKILL.md` and `references/`. Follow the host's Skill installation instructions. **Importing a Skill does not install GitHub MCP, authenticate `gh`, or grant permissions.**

## GitHub backend: choose either

1. **GitHub MCP (preferred):** connect a GitHub MCP integration in your Agent environment and give it appropriate repository permissions. Official project: https://github.com/github/github-mcp-server . MCP toolsets and read-only mode affect exposed capabilities.
2. **GitHub CLI (`gh`):** for a local Agent with shell access, install GitHub CLI (https://cli.github.com/), run `gh auth login` securely on the machine and check `gh auth status`. No MCP required for this path.

InfraKeeper uses the available, authorized path for the requested operation. It never switches backends to evade a policy or security rejection.

## Policy

- **Read automatically:** metadata, files, history, search and checks.
- **Confirm each write:** explicit diff and file scope approval before commits, edits, renames or deletions.
- **Main only:** no branch/PR management, force pushes or history rewriting.
- **Verify:** detect concurrent edits, re-read commits/files, and report partial failures.
- **Evidence:** written records are historical baselines, not live health checks.

## Documents

- [Skill entrypoint](SKILL.md)
- [Backend selection](references/github-backends.md)
- [GitHub MCP integration](references/github-mcp.md)
- [GitHub CLI integration](references/github-cli.md)
- [GitHub workflow / approvals](references/github-workflow.md)

## Current limitations

No tested Hermes-specific installation, no executable end-to-end integration tests, no live SSH/cloud control, and no infrastructure record templates yet. Test write operations first in a disposable repository.

## Security

Never commit secrets, tokens, private keys, raw sensitive logs, or copied private infrastructure as a public example. Restrict Agent and GitHub credentials to the minimum needed permissions.

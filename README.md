# InfraKeeper

InfraKeeper is an experimental, evidence-first infrastructure documentation **Agent Skill**, distributed in a portable **Agent Plugin** wrapper.

## Layout

```text
plugin.json
skills/infra-keeper/
  SKILL.md
  references/
    github-backends.md
    github-mcp.md
    github-cli.md
    github-workflow.md
```

The Skill contains the workflow. The plugin manifest provides a package entry point for hosts that support portable agent plugins. The wrapper does **not** automatically install or authorize GitHub tools.

## Prerequisites

Use **either**:
- An authenticated GitHub MCP integration made available to your agent host (preferred), or
- A locally installed and authenticated GitHub CLI (`gh`) in an agent environment with shell access.

GitHub CLI: https://cli.github.com/ ; GitHub MCP: https://github.com/github/github-mcp-server .

## Policy

InfraKeeper reads and searches repository content automatically; **every mutation requires specific user approval**. Documentation commits go directly to `main`. No branch/PR management, history rewriting, force pushes, or repository administration. After a change, the agent reads back the repository state and reports the result.

See [the Skill](skills/infra-keeper/SKILL.md) and [backend guidance](skills/infra-keeper/references/github-backends.md).

## Installation and validation

Import this repository using your host's **plugin** installer where portable plugins are supported, or install the `skills/infra-keeper/` directory as a standard Agent Skill.

Plugin discovery and runtime behavior vary by host; **Hermes and OpenAI installation are not yet verified end-to-end**. A compatible manifest alone does not guarantee the host installs the package or grants MCP / CLI access.

## Status and scope

This is the GitHub integration foundation, not a live infrastructure operator. No SSH, cloud operations, runtime checks, infrastructure templates, or tested integration suite are included yet.

## Security

Never commit credentials, tokens, private keys, or sensitive logs. Public fixtures must use fictionalized infrastructure. Use minimal GitHub permissions.

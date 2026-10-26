# GitHub backend selection

InfraKeeper supports one GitHub operation backend:

| Backend | Requirements | Best for |
| --- | --- | --- |
| GitHub CLI `gh` | Shell execution, installed `gh`, authenticated account | Local agents, terminals |

## First-time setup

A request to initialize InfraKeeper, configure or connect the CLI, or re-verify a connection belongs
to the [setup wizard](setup-wizard.md), not to this section. The
wizard owns user onboarding, the one-time personal-repository bootstrap and the later read-only
readiness verdict, including the states, the probes and the configuration guidance. Do not restate
those steps here.

The negotiation below covers ordinary documentation work once at least one backend is usable. It
keeps its own rules, and the wizard does not restate them. This version supports only GitHub CLI;
no GitHub MCP, Local Workspace or Local Git backend exists.

## Capability negotiation

1. Resolve repository `OWNER/REPO` from user context — the user's selection, the repository
   established in the conversation, or a stored InfraKeeper binding (`repository` + `branch`) for
   this user — and never guess an unrelated repository. A binding narrows reads to one repository;
   it never authorizes writes and never overrides an exclusion.
2. When local commands are permitted, check `gh --version` and `gh auth status` (never print tokens).
3. Require the bound repository owner to match the authenticated user's GitHub login. Organization,
   collaborator and other-user repositories are outside this backend's scope, even when the account
   has access to them.
4. Prefer the bundled JSON CLI helper for structured operations; use direct `gh` commands only as a disclosed fallback.
5. State the selected CLI path and scope before operations.
6. Backend choice **does not** supersede approval, account permissions, platform rules, branch restrictions, or GitHub protections.

A missing CLI capability can justify using the helper's direct `gh` fallback. A **denied operation** cannot: stop instead of trying another channel to bypass it.

## Common behavioral contract

- `main` only; no branch/PR lifecycle or force-push.
- Automatically read/search/history/status.
- Require concrete, explicit authorization before **every write**.
- Refresh file/version information immediately before an approved write; stop if changed.
- Prefer atomic multi-file updates; otherwise disclose and monitor partial success.
- Verify final GitHub state after committing and report commit SHA.
- Public repositories and Git histories must not receive credentials or sensitive internal configuration.
- Documentation verification is not runtime verification.

See [GitHub CLI](github-cli.md) and [GitHub workflow](github-workflow.md).

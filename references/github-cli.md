# GitHub CLI backend (`gh`)

Official manual: https://cli.github.com/manual/

Use this backend only when the Agent has authorized local command execution and GitHub CLI is installed and authenticated. A local `gh` installation is **optional** when MCP is available.

## Readiness

```sh
gh --version
gh auth status
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef
```

If not authenticated, tell the user to authenticate in their own terminal using `gh auth login` or their host's secure credential mechanism; **never ask them to paste access tokens in chat or commit them**. Check actual repository access with the chosen identity; a successful login alone does not imply write permission. `GH_TOKEN` is supported for noninteractive environments, but credentials must come from a secure external source.

## Read operations (no mutation)

```sh
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef
gh api repos/OWNER/REPO/contents/README.md -f ref=main --method GET
gh api repos/OWNER/REPO/commits?sha=main --method GET
gh api repos/OWNER/REPO/git/trees/main -f recursive=1 --method GET
```

Use `gh api` or permitted local read-only Git commands where appropriate; inspect returned data carefully. Avoid printing authentication headers, sensitive URLs, or secret-bearing raw logs. Check whether the repository actually has a `main` branch before proceeding.

## Writes: approval first

For an approved documentation change, prefer a local checked-out repository and ordinary *non-force* commits when the working tree and branch are known. These are **illustrative**, not unattended commands:

```sh
git status --short
git branch --show-current
git fetch origin main
git status --porcelain
# review the approved diff and confirm the current main has not changed
git diff --check
git diff -- path/to/approved-file.md
# stage only explicitly approved paths; commit and push only after approval
git add -- path/to/approved-file.md
git commit -m "docs: update approved infrastructure record"
git push origin main
```

Do not run `git add -A`, `git push --force`, or commit unrelated local changes. If the tree is dirty, `main` differs from the expected upstream, or a concurrent update occurs, stop and reassess. Verify remote files and the final commit via GitHub read operations after pushing.

Alternatively, a client may use approved `gh api` GitHub Contents API or Git Tree/Commit API calls, but must respect version SHA preconditions and partial-update risks. Never encode secret values into shell command arguments, files or logs.

## Restrictions

The following are disabled by InfraKeeper policy even if `gh` could execute them: branch creation/deletion, pull requests, force pushes, history rewriting, repository settings/visibility changes, and privilege escalation. If GitHub or the tool host blocks a write, **stop**; do not try another backend to bypass the rejection.

Official references:
- https://cli.github.com/manual/gh_auth_status
- https://cli.github.com/manual/gh_api
- https://cli.github.com/manual/gh_repo_view

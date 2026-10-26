# GitHub CLI setup wizard acceptance script

**Status: Not Run.** This is a manual acceptance script, not an execution result. No case below is
complete until an operator runs it and records redacted evidence.

## Scope

This version has one backend: the local GitHub CLI (`gh`). The setup wizard must not configure or
inspect credentials, shell profiles or repository content before the user names a repository. It
may give OS-specific installation and login guidance, or execute one exact command after separate
approval. It must never write GitHub content, silently install `gh` or request a token in chat.

## Evidence rules

- Record command names, exit status and redacted output only.
- Never record tokens, authorization headers, passwords, raw environment values or private paths.
- A repository-level `ready` verdict requires a personal `OWNER/REPO` and `main` to be read successfully.
- An HTTP `404` is `unverified`, not proof of insufficient permissions.
- A first run with no binding may have exactly one approved repository-creation call; later setup
  runs must have zero GitHub write calls.

## Cases

| ID | Condition | Expected result |
| --- | --- | --- |
| T1 | Start setup with local commands available and authenticated `gh` | `gh` capability and identity are detected; no repository is read before a name is chosen |
| T2 | `gh` is not installed | `unavailable`; ask for the OS, show the exact official command and request separate approval |
| T3 | User declines the install approval | do not run a package-manager command; keep `unavailable` and offer the user-run path |
| T4 | User approves the exact install command | execute only that command once in the Agent page when supported, then re-run `gh --version` |
| T5 | `gh auth status` reports no login | `unauthenticated`; show `gh auth login` and request separate approval before starting it in the Agent page |
| T6 | User completes browser/device authorization | re-run `gh auth status`; no token appears in the transcript |
| T7 | `gh auth status` succeeds and no binding exists | ask for a name, default `infrastructure`; do not report repository `ready` yet |
| T8 | Chosen personal repository name already exists | ask for a different unused name; do not bind or overwrite it |
| T9 | Chosen personal repository name is unused and user approves bootstrap | run exactly one `gh repo create OWNER/REPO --private --add-readme`, then read back metadata and the initial commit |
| T10 | Stored binding exists on a later setup run | skip creation and name selection; verify only the bound repository and `main` |
| T11 | Bind an organization, collaborator or other-user repository | report `out-of-scope`; zero reads against that repository |
| T12 | Bind a nonexistent or ambiguous repository owned by the user | report `unverified`; do not try another repository |
| T13 | Read returns explicit `403` | report `insufficient-permissions`; stop and do not retry through another channel |
| T14 | `main` does not exist | report the missing branch; do not create or substitute a branch |
| T15 | Interrupt setup and start again | no unapproved repository content or host credential state was written; restart from capability scan |
| T16 | Run setup with a user-declared excluded repository | zero reads against the excluded repository |
| T17 | Complete any setup run | no token appears in transcript or record; later runs have zero GitHub write calls |

## Required summary

```text
InfraKeeper setup — summary
backend selected: cli
repository: OWNER/REPO (main, private)
cli: ready (read access verified)
bootstrap: created in this run / reused existing binding
outstanding: device audit (not implemented in this version)
```

The summary must state whether this was a first-run repository bootstrap. If so, report the exact
approved creation command and resulting initial commit separately; otherwise report that no GitHub
write occurred. Also report any exact approved local installation or login command. A setup result is
not evidence of write permission or live infrastructure health.

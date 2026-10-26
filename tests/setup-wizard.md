# GitHub CLI setup wizard acceptance script

**Status: Not Run.** This is a manual acceptance script, not an execution result. No case below is
complete until an operator runs it and records redacted evidence.

## Scope

This version has one backend: the local GitHub CLI (`gh`). The setup wizard must not configure or
inspect credentials, shell profiles or repository content before the user names a repository.
It must never write GitHub content, create a test commit, install `gh` or request a token in chat.

## Evidence rules

- Record command names, exit status and redacted output only.
- Never record tokens, authorization headers, passwords, raw environment values or private paths.
- A repository-level `ready` verdict requires the user to name the exact `OWNER/REPO` and `main` to
  be read successfully.
- An HTTP `404` is `unverified`, not proof of insufficient permissions.
- Any write call count must remain zero for the whole setup run.

## Cases

| ID | Condition | Expected result |
| --- | --- | --- |
| T1 | Start setup with local commands available and authenticated `gh` | `gh` capability is detected; no repository is read before binding |
| T2 | `gh` is not installed | `unavailable`; point to the official install page; do not install automatically |
| T3 | `gh auth status` reports no login | `unauthenticated`; instruct the user to run `gh auth login` in their own terminal |
| T4 | `gh auth status` succeeds but no repository is named | identity readiness only; do not report repository `ready` |
| T5 | Bind a readable `OWNER/REPO` with `main` | read metadata and root listing; report `ready` with the exact scope |
| T6 | Bind a nonexistent or ambiguous repository | report `unverified`; do not try another repository |
| T7 | Read returns explicit `403` | report `insufficient-permissions`; stop and do not retry through another channel |
| T8 | `main` does not exist | report the missing branch; do not create or substitute a branch |
| T9 | Interrupt setup and start again | no repository content or host credential state was written; restart from capability scan |
| T10 | Run setup with a user-declared excluded repository | zero reads against the excluded repository |
| T11 | Complete any setup run | zero GitHub write calls; no token appears in transcript or record |

## Required summary

```text
InfraKeeper setup — summary
backend selected: cli
repository: OWNER/REPO (main, private)
cli: ready (read access verified)
outstanding: device audit (not implemented in this version)
```

The summary must state that no repository content, authentication state or host configuration was
changed. A setup result is not evidence of write permission or live infrastructure health.

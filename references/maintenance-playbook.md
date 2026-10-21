# Maintenance playbook

## Diagnosis

Begin by defining the symptom and its boundary: user-visible behavior, affected service, time window, and known recent changes. Then compare it with the documented dependency path.

Propose low-risk checks first. Examples include a service status query, a log window with secrets redacted, a local port listener check, or a provider health page. Explain what each check would prove. Do not present an unverified hypothesis as a root cause.

Stop and request direction when diagnosis needs credentials, a production change, an ambiguous recovery action, or access that the user has not authorized.

## Change plan

Every meaningful change should cover:

1. **Compatibility:** existing services, ports, route ownership, resources, dependencies, and timing.
2. **Pre-change state:** what will be checked or backed up before starting.
3. **Implementation:** smallest reversible steps, with parameters supplied by the owner rather than invented.
4. **Validation:** a concrete success signal, including scope and time window.
5. **Rollback:** the trigger, action, and safe restoration point.
6. **Record update:** exact documentation pages to update and which evidence date to add.

## Incident notes

During an incident, favor service restoration and evidence preservation over cleanup. Record timestamps, affected scope, observation source, actions taken, and outcome. Do not put raw secrets or private logs into an issue, repository, or chat transcript.

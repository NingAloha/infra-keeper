# orbit-01 — fictional edge node

Role: publish a small public status page for Northstar Studio. Baseline reviewed: 2026-01-15.

## Index

- [System](system.md)
- [Network](network.md)
- [Services](services/status-page.md)
- [Operations](operations.md)

## Relationships

The `status-page` service depends on the node's ingress and the route recorded in `../../domains/routing.md`. The record intentionally does not assert live service health.

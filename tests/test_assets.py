#!/usr/bin/env python3
"""Offline release checks for the InfraKeeper skill and its safe sample assets."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "infrastructure"
EVALUATIONS = ROOT / "evaluations" / "cases.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def all_text_files() -> list[Path]:
    return [path for path in ROOT.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".yaml"}]


def require_files() -> None:
    required = [
        ROOT / "SKILL.md", ROOT / "README.md", ROOT / "LICENSE", ROOT / "agents" / "openai.yaml",
        TEMPLATE / "README.md", TEMPLATE / "domains" / "routing.md",
        TEMPLATE / "devices" / "_device-template" / "README.md",
        TEMPLATE / "devices" / "_device-template" / "system.md",
        TEMPLATE / "devices" / "_device-template" / "network.md",
        TEMPLATE / "devices" / "_device-template" / "operations.md",
        TEMPLATE / "devices" / "_device-template" / "services" / "README.md", EVALUATIONS,
        TEMPLATE / "devices" / "_device-template" / "services" / "_service-template.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        fail("required files are missing: " + ", ".join(missing))


def reject_secret_like_content() -> None:
    patterns = {
        "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "GitHub personal token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
        "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    }
    violations: list[str] = []
    for path in all_text_files():
        content = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            if pattern.search(content):
                violations.append(f"{path.relative_to(ROOT)} contains {label}")
    if violations:
        fail("; ".join(violations))


def validate_evaluations() -> None:
    data = json.loads(EVALUATIONS.read_text(encoding="utf-8"))
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 4:
        fail("evaluations must contain at least four scenarios")
    identifiers = set()
    for case in cases:
        required = ("id", "request", "repository_fixture", "must_do", "must_not_do")
        if any(not case.get(field) for field in required):
            fail("each evaluation needs id, request, fixture, must_do, and must_not_do")
        if case["id"] in identifiers:
            fail(f"duplicate evaluation id: {case['id']}")
        identifiers.add(case["id"])


def main() -> None:
    require_files()
    reject_secret_like_content()
    validate_evaluations()
    print("PASS: InfraKeeper release assets are complete and free of common secret patterns.")


if __name__ == "__main__":
    main()

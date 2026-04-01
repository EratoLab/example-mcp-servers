from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoFile:
    name: str
    title: str
    required_tags: frozenset[str]
    content: str


FILES: tuple[DemoFile, ...] = (
    DemoFile(
        name="welcome.md",
        title="Welcome",
        required_tags=frozenset({"public"}),
        content="This OIDC demo server exposes different files by user email claim.",
    ),
    DemoFile(
        name="faq.md",
        title="FAQ",
        required_tags=frozenset({"public"}),
        content="Public questions cover startup, transport mode, and authentication headers.",
    ),
    DemoFile(
        name="service-status.txt",
        title="Service Status",
        required_tags=frozenset({"public"}),
        content="Status: green. Demo services are operating normally.",
    ),
    DemoFile(
        name="eng-backlog.md",
        title="Engineering Backlog",
        required_tags=frozenset({"engineering"}),
        content="Open items: schema validation, retries, and deployment packaging.",
    ),
    DemoFile(
        name="ops-runbook.md",
        title="Operations Runbook",
        required_tags=frozenset({"operations"}),
        content="First action: confirm scope, then gather logs and recent deploy details.",
    ),
    DemoFile(
        name="finance-pipeline.csv",
        title="Finance Pipeline",
        required_tags=frozenset({"finance"}),
        content="account,stage,amount\nNorthwind,trial,9000\nContoso,contract,18000",
    ),
    DemoFile(
        name="leadership-notes.md",
        title="Leadership Notes",
        required_tags=frozenset({"leadership"}),
        content="Enterprise expansion depends on tighter onboarding and observability.",
    ),
    DemoFile(
        name="security-checklist.md",
        title="Security Checklist",
        required_tags=frozenset({"security"}),
        content="Rotate secrets, validate JWT issuer, and capture authorization decisions.",
    ),
    DemoFile(
        name="change-window.txt",
        title="Change Window",
        required_tags=frozenset({"operations"}),
        content="Preferred maintenance window: Tuesdays 20:00-22:00 UTC.",
    ),
    DemoFile(
        name="incident-digest.md",
        title="Incident Digest",
        required_tags=frozenset({"security"}),
        content="Recent security incidents: none; latest drill completed successfully.",
    ),
)

FILES_BY_NAME = {demo_file.name: demo_file for demo_file in FILES}


def list_visible_files(allowed_tags: set[str]) -> list[DemoFile]:
    return [demo_file for demo_file in FILES if demo_file.required_tags.issubset(allowed_tags)]

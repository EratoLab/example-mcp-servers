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
        name="company-overview.md",
        title="Company Overview",
        required_tags=frozenset({"public"}),
        content="Erato Files Demo\n\nA small example repository for MCP authorization demos.",
    ),
    DemoFile(
        name="support-playbook.md",
        title="Support Playbook",
        required_tags=frozenset({"public"}),
        content="Escalate incidents with a ticket number and a short impact summary.",
    ),
    DemoFile(
        name="release-notes.txt",
        title="Release Notes",
        required_tags=frozenset({"public"}),
        content="Version 0.1.0 introduces two demo MCP authentication patterns.",
    ),
    DemoFile(
        name="engineering-roadmap.md",
        title="Engineering Roadmap",
        required_tags=frozenset({"engineering"}),
        content="Q2 priorities: deployment hardening, tracing, and template automation.",
    ),
    DemoFile(
        name="system-architecture.md",
        title="System Architecture",
        required_tags=frozenset({"engineering"}),
        content="The platform is split into API, worker, and retrieval services.",
    ),
    DemoFile(
        name="incident-retrospective.md",
        title="Incident Retrospective",
        required_tags=frozenset({"operations"}),
        content="Root cause: a missing timeout on a downstream service dependency.",
    ),
    DemoFile(
        name="team-oncall.txt",
        title="On-call Rotation",
        required_tags=frozenset({"operations"}),
        content="Primary: platform-team@example.com; secondary: sre@example.com.",
    ),
    DemoFile(
        name="finance-forecast.csv",
        title="Finance Forecast",
        required_tags=frozenset({"finance"}),
        content="quarter,revenue\nQ2,125000\nQ3,131000\nQ4,145000",
    ),
    DemoFile(
        name="security-audit.md",
        title="Security Audit",
        required_tags=frozenset({"security"}),
        content="Findings: rotate demo credentials and tighten access logging coverage.",
    ),
    DemoFile(
        name="board-summary.md",
        title="Board Summary",
        required_tags=frozenset({"leadership"}),
        content="Monthly summary: usage is up, and enterprise pilots remain on schedule.",
    ),
)

FILES_BY_NAME = {demo_file.name: demo_file for demo_file in FILES}


def list_visible_files(allowed_tags: set[str]) -> list[DemoFile]:
    return [demo_file for demo_file in FILES if demo_file.required_tags.issubset(allowed_tags)]

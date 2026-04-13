from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoFile:
    name: str
    title: str
    requires_admin_scope: bool
    content: str


FILES: tuple[DemoFile, ...] = (
    DemoFile(
        name="welcome.md",
        title="Welcome",
        requires_admin_scope=False,
        content="This server uses Keycloak-backed OAuth2 to protect FastMCP tools.",
    ),
    DemoFile(
        name="roadmap.md",
        title="Product Roadmap",
        requires_admin_scope=False,
        content="Upcoming work: rollout metrics, regional data residency, and audit exports.",
    ),
    DemoFile(
        name="service-catalog.csv",
        title="Service Catalog",
        requires_admin_scope=False,
        content="service,owner,tier\nbilling,finance,1\nsearch,platform,1\nsupport,ops,2",
    ),
    DemoFile(
        name="oncall-notes.md",
        title="On-call Notes",
        requires_admin_scope=False,
        content="Primary escalation path: platform on-call, then incident commander.",
    ),
    DemoFile(
        name="admin-audit-log.md",
        title="Admin Audit Log",
        requires_admin_scope=True,
        content="Admin-only: token audience checks passed for the last audit window.",
    ),
    DemoFile(
        name="key-rotation-plan.md",
        title="Key Rotation Plan",
        requires_admin_scope=True,
        content="Admin-only: rotate realm keys after staging validation and JWKS cache expiry.",
    ),
)

FILES_BY_NAME = {demo_file.name: demo_file for demo_file in FILES}

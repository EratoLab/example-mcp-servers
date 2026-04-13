from __future__ import annotations

import os

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.auth import RemoteAuthProvider, require_scopes
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from .config import Settings, load_settings
from .files import FILES, FILES_BY_NAME, DemoFile


def _has_scope(scope_name: str, scopes: list[str]) -> bool:
    return scope_name in scopes


def _visible_files(settings: Settings, scopes: list[str]) -> list[DemoFile]:
    has_admin_scope = _has_scope(settings.mcp_admin_scope, scopes)
    return [
        demo_file
        for demo_file in FILES
        if not demo_file.requires_admin_scope or has_admin_scope
    ]


def create_server(settings: Settings | None = None) -> FastMCP:
    settings = settings or load_settings()

    token_verifier = JWTVerifier(
        jwks_uri=settings.jwks_uri,
        issuer=settings.issuer_url,
        audience=settings.audience,
    )
    auth_provider = RemoteAuthProvider(
        token_verifier=token_verifier,
        authorization_servers=[settings.issuer_url],
        base_url=settings.server_base_url,
        allowed_client_redirect_uris=list(settings.allowed_client_redirect_uris),
        scopes_supported=[settings.mcp_tools_scope, settings.mcp_admin_scope],
    )

    server = FastMCP(name="OAuth2 Keycloak DCR File Server", auth=auth_provider)

    @server.tool(auth=require_scopes(settings.mcp_tools_scope))
    def whoami() -> dict[str, object]:
        """Show the current token subject, audience, issuer, and scopes."""
        token = get_access_token()
        if token is None:
            raise ToolError("No access token is available in the current request.")

        return {
            "client_id": token.client_id,
            "subject": token.claims.get("sub"),
            "preferred_username": token.claims.get("preferred_username"),
            "email": token.claims.get("email"),
            "issuer": token.claims.get("iss"),
            "audience": token.claims.get("aud"),
            "scopes": token.scopes,
        }

    @server.tool(auth=require_scopes(settings.mcp_tools_scope))
    def list_files() -> list[dict[str, object]]:
        """List the files visible to the caller's current OAuth scopes."""
        token = get_access_token()
        if token is None:
            raise ToolError("No access token is available in the current request.")

        return [
            {
                "name": demo_file.name,
                "title": demo_file.title,
                "requires_admin_scope": demo_file.requires_admin_scope,
            }
            for demo_file in _visible_files(settings, token.scopes)
        ]

    @server.tool(auth=require_scopes(settings.mcp_tools_scope))
    def get_file(name: str) -> dict[str, object]:
        """Return a file, enforcing the extra mcp:admin scope for admin content."""
        token = get_access_token()
        if token is None:
            raise ToolError("No access token is available in the current request.")

        demo_file = FILES_BY_NAME.get(name)
        if demo_file is None:
            raise ToolError(f"Unknown file: {name}")

        if demo_file.requires_admin_scope and not _has_scope(settings.mcp_admin_scope, token.scopes):
            raise ToolError(
                f"Access denied for file: {name}. The {settings.mcp_admin_scope!r} scope is required."
            )

        return {
            "name": demo_file.name,
            "title": demo_file.title,
            "requires_admin_scope": demo_file.requires_admin_scope,
            "content": demo_file.content,
            "scopes": token.scopes,
            "subject": token.claims.get("sub"),
        }

    return server


def main() -> None:
    settings = load_settings()
    create_server(settings).run(
        transport=os.getenv("OAUTH2_SERVER_TRANSPORT", "streamable-http"),
        host=settings.host,
        port=settings.port,
    )

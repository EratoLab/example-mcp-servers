from __future__ import annotations

import os
from dataclasses import dataclass


def _normalize_base_url(url: str) -> str:
    return url.rstrip("/")


def _split_patterns(raw_value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in raw_value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    server_base_url: str
    mcp_path: str
    keycloak_base_url: str
    keycloak_realm: str
    audience: str
    issuer_url: str
    jwks_uri: str
    mcp_tools_scope: str
    mcp_admin_scope: str
    allowed_client_redirect_uris: tuple[str, ...]


def load_settings() -> Settings:
    host = os.getenv("OAUTH2_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("OAUTH2_SERVER_PORT", "8003"))
    server_base_url = _normalize_base_url(
        os.getenv("OAUTH2_SERVER_BASE_URL", f"http://{host}:{port}")
    )
    mcp_path = os.getenv("OAUTH2_SERVER_MCP_PATH", "/mcp")
    keycloak_base_url = _normalize_base_url(os.getenv("KEYCLOAK_BASE_URL", "http://127.0.0.1:8080"))
    keycloak_realm = os.getenv("KEYCLOAK_REALM", "mcp-demo")
    issuer_url = f"{keycloak_base_url}/realms/{keycloak_realm}"
    allowed_redirects = _split_patterns(
        os.getenv(
            "OAUTH2_ALLOWED_CLIENT_REDIRECT_URIS",
            "http://127.0.0.1:*,http://localhost:*",
        )
    )

    return Settings(
        host=host,
        port=port,
        server_base_url=server_base_url,
        mcp_path=mcp_path,
        keycloak_base_url=keycloak_base_url,
        keycloak_realm=keycloak_realm,
        audience=os.getenv("OAUTH2_SERVER_AUDIENCE", f"{server_base_url}{mcp_path}"),
        issuer_url=issuer_url,
        jwks_uri=os.getenv("KEYCLOAK_JWKS_URI", f"{issuer_url}/protocol/openid-connect/certs"),
        mcp_tools_scope=os.getenv("MCP_TOOLS_SCOPE", "mcp:tools"),
        mcp_admin_scope=os.getenv("MCP_ADMIN_SCOPE", "mcp:admin"),
        allowed_client_redirect_uris=allowed_redirects,
    )

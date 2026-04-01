from __future__ import annotations

import os

import jwt
from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext

from .config import OidcSettings, load_settings
from .files import FILES, FILES_BY_NAME

PUBLIC_FILES = {
    demo_file.name for demo_file in FILES if "public" in demo_file.required_tags
}


def _validate_id_token(token: str, settings: OidcSettings) -> dict[str, object]:
    payload = jwt.decode(
        token,
        settings.shared_secret,
        algorithms=[settings.algorithm],
        issuer=settings.issuer,
        audience=list(settings.audiences),
        options={"require": ["iss", "aud", "iat", "exp", "email", "groups"]},
        leeway=settings.clock_skew_seconds,
    )
    return dict(payload)


class OidcGroupAccessMiddleware(Middleware):
    def __init__(self, settings: OidcSettings) -> None:
        self.settings = settings

    async def on_request(self, context: MiddlewareContext, call_next):
        headers = get_http_headers(include={"authorization"}) or {}
        authorization = headers.get("authorization", "")
        state = context.fastmcp_context

        if state:
            state.set_state("allowed_files", set(PUBLIC_FILES))
            state.set_state("auth_attempted", False)
            state.set_state("auth_error", None)
            state.set_state("principal_email", None)
            state.set_state("principal_groups", [])

        if not authorization:
            return await call_next(context)

        if not authorization.lower().startswith("bearer "):
            if state:
                state.set_state("auth_attempted", True)
                state.set_state("auth_error", "Authorization header must use the Bearer scheme.")
            return await call_next(context)

        token = authorization.split(" ", 1)[1].strip()

        try:
            payload = _validate_id_token(token, self.settings)
        except jwt.InvalidTokenError as exc:
            if state:
                state.set_state("auth_attempted", True)
                state.set_state("auth_error", f"Invalid ID token: {exc}")
            return await call_next(context)

        email = str(payload["email"]).lower()
        groups_claim = payload["groups"]
        if not isinstance(groups_claim, list) or not all(isinstance(group, str) for group in groups_claim):
            if state:
                state.set_state("auth_attempted", True)
                state.set_state("principal_email", email)
                state.set_state("auth_error", "The ID token groups claim must be a list of strings.")
            return await call_next(context)

        matched_groups = [group for group in groups_claim if group in self.settings.groups]
        allowed_files = set(PUBLIC_FILES)
        for group in matched_groups:
            allowed_files.update(self.settings.groups[group].allowed_files)

        if state:
            state.set_state("auth_attempted", True)
            state.set_state("principal_email", email)
            state.set_state("auth_error", None)
            state.set_state("principal_groups", list(groups_claim))
            state.set_state("allowed_files", allowed_files)

        return await call_next(context)


def _get_allowed_files(ctx: Context) -> set[str]:
    allowed_files = ctx.get_state("allowed_files")
    if isinstance(allowed_files, set):
        return allowed_files
    return set(PUBLIC_FILES)


def _raise_if_invalid_token(ctx: Context) -> None:
    auth_attempted = ctx.get_state("auth_attempted")
    auth_error = ctx.get_state("auth_error")
    if auth_attempted and auth_error:
        raise ToolError(str(auth_error))


def create_server() -> FastMCP:
    config_path = os.getenv("OIDC_CONFIG_PATH", "oidc-config.toml")
    settings = load_settings(config_path)
    server = FastMCP(name="OIDC ID Token File Server")
    server.add_middleware(OidcGroupAccessMiddleware(settings=settings))

    @server.tool
    def list_files(ctx: Context) -> list[dict[str, object]]:
        """List the dummy files visible to the current caller."""
        _raise_if_invalid_token(ctx)
        return [
            {
                "name": demo_file.name,
                "title": demo_file.title,
                "required_tags": sorted(demo_file.required_tags),
            }
            for demo_file in FILES
            if demo_file.name in _get_allowed_files(ctx)
        ]

    @server.tool
    def get_file(name: str, ctx: Context) -> dict[str, object]:
        """Return a dummy file if the current caller is authorized to see it."""
        _raise_if_invalid_token(ctx)

        demo_file = FILES_BY_NAME.get(name)
        if demo_file is None:
            raise ToolError(f"Unknown file: {name}")

        if demo_file.name not in _get_allowed_files(ctx):
            raise ToolError(f"Access denied for file: {name}")

        return {
            "name": demo_file.name,
            "title": demo_file.title,
            "required_tags": sorted(demo_file.required_tags),
            "content": demo_file.content,
            "principal_email": ctx.get_state("principal_email"),
            "principal_groups": ctx.get_state("principal_groups"),
        }

    return server


def main() -> None:
    host = os.getenv("OIDC_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("OIDC_SERVER_PORT", "8002"))
    create_server().run(transport="streamable-http", host=host, port=port)

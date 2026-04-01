from __future__ import annotations

import os

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext

from .files import FILES_BY_NAME, list_visible_files

DEFAULT_API_KEY = "demo-erato-api-key"
PUBLIC_TAGS = {"public"}
FULL_ACCESS_TAGS = {"public", "engineering", "operations", "finance", "security", "leadership"}


class ApiKeyAccessMiddleware(Middleware):
    def __init__(self, valid_api_key: str) -> None:
        self.valid_api_key = valid_api_key

    async def on_request(self, context: MiddlewareContext, call_next):
        headers = get_http_headers(include={"x-api-key"}) or {}
        supplied_api_key = headers.get("x-api-key")

        access_tags = FULL_ACCESS_TAGS if supplied_api_key == self.valid_api_key else PUBLIC_TAGS
        access_level = "full" if supplied_api_key == self.valid_api_key else "public"

        if context.fastmcp_context:
            context.fastmcp_context.set_state("access_tags", set(access_tags))
            context.fastmcp_context.set_state("access_level", access_level)

        return await call_next(context)


def _get_access_tags(ctx: Context) -> set[str]:
    access_tags = ctx.get_state("access_tags")
    if isinstance(access_tags, set):
        return access_tags
    return set(PUBLIC_TAGS)


mcp = FastMCP(name="API Key File Server")
mcp.add_middleware(ApiKeyAccessMiddleware(valid_api_key=os.getenv("API_KEY_SERVER_KEY", DEFAULT_API_KEY)))


@mcp.tool
def list_files(ctx: Context) -> list[dict[str, object]]:
    """List the dummy files visible to the current caller."""
    return [
        {
            "name": demo_file.name,
            "title": demo_file.title,
            "required_tags": sorted(demo_file.required_tags),
        }
        for demo_file in list_visible_files(_get_access_tags(ctx))
    ]


@mcp.tool
def get_file(name: str, ctx: Context) -> dict[str, object]:
    """Return a dummy file if the current caller is authorized to see it."""
    demo_file = FILES_BY_NAME.get(name)
    if demo_file is None:
        raise ToolError(f"Unknown file: {name}")

    if not demo_file.required_tags.issubset(_get_access_tags(ctx)):
        raise ToolError(f"Access denied for file: {name}")

    return {
        "name": demo_file.name,
        "title": demo_file.title,
        "required_tags": sorted(demo_file.required_tags),
        "content": demo_file.content,
    }


def main() -> None:
    host = os.getenv("API_KEY_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("API_KEY_SERVER_PORT", "8001"))
    mcp.run(transport="streamable-http", host=host, port=port)

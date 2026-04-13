# API Key File Server

This example shows a simple fixed API-key authentication model for a FastMCP server.
Without the correct `X-Api-Key`, callers can only see public demo files. With the
configured key, all baked-in files become visible.

## Commands

```bash
just install
just run
```

For interactive testing, you can inspect the server with the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

```bash
npx @modelcontextprotocol/inspector
```

Then connect to `http://127.0.0.1:8001/mcp` and add `X-Api-Key: demo-erato-api-key` if you want full access.

The server listens on `http://127.0.0.1:8001/mcp` by default. Override with
`API_KEY_SERVER_HOST`, `API_KEY_SERVER_PORT`, or `API_KEY_SERVER_KEY`.

The default demo key is:

```text
demo-erato-api-key
```

## Erato Docs

- General MCP server docs: https://erato.chat/docs/features/mcp_servers
- Relevant authentication method: fixed authentication in the configuration reference: https://erato.chat/docs/configuration#mcp_serversserver_idauthentication

## Erato Configuration

Example `erato.toml` block without the API key, which will expose only public files:

```toml
[mcp_servers.template_api_key_public]
transport_type = "streamable_http"
url = "http://127.0.0.1:8001/mcp"
```

Example `erato.toml` block with full access:

```toml
[mcp_servers.template_api_key_full]
transport_type = "streamable_http"
url = "http://127.0.0.1:8001/mcp"
additional_request_headers = ["X-Api-Key=demo-erato-api-key"]
```

## Tool Behavior

- `list_files` returns only the files currently visible to the caller
- `get_file(name=...)` returns file contents or raises an authorization error if the file is not visible to the caller

# OAuth2 Keycloak DCR Server

This example shows a FastMCP server acting as an OAuth2-protected resource
server for Erato's native OAuth2 authentication mode. It uses FastMCP's
`RemoteAuthProvider` to expose MCP/OAuth discovery metadata, validates JWT
access tokens issued by Keycloak, and gates some files behind an extra
`mcp:admin` scope.

The repository also includes a dockerized Keycloak setup that bootstraps a demo
realm, scopes, a demo user, and a local development client for Erato.

## What This Example Highlights

- MCP protected-resource metadata (`/.well-known/oauth-protected-resource`)
- OAuth 2.0 / OIDC discovery via Keycloak
- Dynamic client registration using Keycloak's client registration API
- Audience-bound JWT access tokens validated locally through Keycloak JWKS
- Erato-managed OAuth2 for MCP servers, including dynamic client registration

## Commands

```bash
docker compose up -d keycloak keycloak-bootstrap
just install
just run
```

For interactive testing, you can inspect the server with the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

```bash
npx @modelcontextprotocol/inspector
```

Then connect to `http://127.0.0.1:8003/mcp`. Use the inspector together with a valid Keycloak-issued bearer token when you want to exercise the protected tools.

The MCP server listens on `http://127.0.0.1:8003/mcp` by default.

Override with:

- `OAUTH2_SERVER_HOST`
- `OAUTH2_SERVER_PORT`
- `OAUTH2_SERVER_BASE_URL`
- `KEYCLOAK_BASE_URL`
- `KEYCLOAK_REALM`

## Keycloak Bootstrap

`docker compose up -d keycloak keycloak-bootstrap` creates:

- realm: `mcp-demo`
- demo user: `erato-demo`
- demo password: `erato-demo-password`
- optional OAuth scopes: `mcp:tools`, `mcp:admin`
- pre-registered client for Erato: `erato-local-dev`

The bootstrap is designed to avoid Keycloak UI work for the normal local flow.

## Dynamic Client Registration

This project keeps the tutorial's DCR idea but avoids environment-specific
anonymous-registration UI setup by using Keycloak's registration API through
`kcreg.sh`.

Register a new client dynamically:

```bash
./scripts/register_dynamic_client.sh my-mcp-client
```

The script runs `kcreg.sh` inside the Keycloak container, authenticates as the
bootstrap admin user, and creates a public client with localhost redirect URIs.

If you specifically want browser-origin anonymous DCR like in the MCP tutorial,
you can additionally configure Keycloak's client-registration policies in the
admin UI. For the local Erato flow below, that is not required.

## Erato Docs

- General MCP server docs: https://erato.chat/docs/features/mcp_servers
- Relevant authentication method: OAuth2 authentication in the configuration reference: https://erato.chat/docs/configuration#mcp_serversserver_idauthentication

## Erato Configuration

Erato's MCP authentication docs use a native OAuth2 mode for remote MCP
servers. That is the intended integration for this project.

Before enabling this server in Erato, make sure `server.encryption_key` is set
in your Erato configuration so OAuth client and token state can be stored
securely.

Example `erato.toml` block using dynamic client registration:

```toml
[mcp_servers.keycloak_oauth_demo]
transport_type = "streamable_http"
url = "http://127.0.0.1:8003/mcp"

[mcp_servers.keycloak_oauth_demo.authentication]
mode = "oauth2"

[mcp_servers.keycloak_oauth_demo.authentication.oauth2]
client_name = "Erato Keycloak MCP Demo"
scopes = ["openid", "mcp:tools", "mcp:admin"]
```

Example `erato.toml` block using the bootstrap-created client:

```toml
[mcp_servers.keycloak_oauth_demo]
transport_type = "streamable_http"
url = "http://127.0.0.1:8003/mcp"

[mcp_servers.keycloak_oauth_demo.authentication]
mode = "oauth2"

[mcp_servers.keycloak_oauth_demo.authentication.oauth2]
client_id = "erato-local-dev"
scopes = ["openid", "mcp:tools", "mcp:admin"]
```

If you later convert that Keycloak client into a confidential client, add
`client_secret` in the same block.

## Manual Token Testing

The helper below is still useful when you want to validate the Keycloak realm
and MCP server outside Erato:

```bash
./scripts/get_erato_access_token.sh
```

By default, that script requests both `mcp:tools` and `mcp:admin`. To request
only the basic scope:

```bash
MCP_SCOPE="openid mcp:tools" ./scripts/get_erato_access_token.sh
```

## Tool Behavior

- `whoami` shows the validated token subject, audience, and scopes
- `list_files` shows all regular files with `mcp:tools`, and includes admin
  files when the token also contains `mcp:admin`
- `get_file(name=...)` returns file contents and enforces the same scope rules

## Notes

- This example follows the MCP authorization tutorial's Keycloak-based resource
  server pattern while using FastMCP's built-in remote OAuth support.
- For Erato, the intended setup is
  `mcp_servers.<server_id>.authentication.mode = "oauth2"`, not static
  `http_headers`.
- Keycloak does not yet support OAuth 2.0 Resource Indicators as MCP expects
  for newer spec revisions, so this example follows the documented workaround
  of binding the audience through requested scopes.

# OIDC ID Token File Server

This example shows group-based authorization based on an OIDC-style ID token in
the `Authorization: Bearer ...` header. The server validates the token as a JWT,
reads its issuer, accepted audiences, signing key, and group-to-file mapping
from a TOML configuration file, and then exposes only the files allowed for the
token's `groups` claim.

## Commands

```bash
cp oidc-config.template.toml oidc-config.toml
just install
just run
```

For interactive testing, you can inspect the server with the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

```bash
npx @modelcontextprotocol/inspector
```

Then connect to `http://127.0.0.1:8002/mcp` and provide an `Authorization: Bearer ...` header with a valid ID token when you want to test group-based access.

The server listens on `http://127.0.0.1:8002/mcp` by default. Override with
`OIDC_SERVER_HOST`, `OIDC_SERVER_PORT`, or `OIDC_CONFIG_PATH`.

## Configuration File

The project includes `oidc-config.template.toml`. Copy it to
`oidc-config.toml` and adjust it for the issuer, audiences, and signing key you
want to use.

The template defines three known groups:

- `finance-team`
- `engineering-team`
- `security-team`

Each group grants a different set of file names. The server unions the allowed
files from all configured groups present in the token's `groups` claim, plus
the always-visible public files.

This is the important authorization boundary for the example: the MCP server
does not decide which user belongs to which group. That decision is delegated to
the authorization server or identity provider that issues the ID token. To
change which users can see which files, change the user's group memberships in
the upstream identity system so it emits different `groups` claims. The server
only maps group names to file names; user-to-group assignment should remain in
the IdP.

## Minting Demo Tokens

For local testing, this repository includes a helper script:

```bash
uv run python scripts/mint_test_token.py alice@example.com
```

That script reads `oidc-config.toml`, creates a short-lived HS256 token, and
prints it to stdout. Pass a second argument to choose a specific audience from
the configured list, and an optional third argument with a comma-separated
groups list such as `engineering-team,security-team`.

## Erato Docs

- General MCP server docs: https://erato.chat/docs/features/mcp_servers
- Relevant authentication method: forwarded authentication in the configuration reference: https://erato.chat/docs/configuration#mcp_serversserver_idauthentication

## Erato Configuration

Example `erato.toml` block:

```toml
[mcp_servers.template_oidc]
transport_type = "streamable_http"
url = "http://127.0.0.1:8002/mcp"
additional_request_headers = ["Authorization=Bearer <paste-id-token-here>"]
```

Use an ID token whose `aud` claim matches one of the configured audiences in
`oidc-config.toml`, and whose `groups` claim contains the group names that
should grant access.

## Tool Behavior

- `list_files` returns only the files visible to the current token groups
- `get_file(name=...)` returns file contents or raises an authorization error
- missing tokens fall back to public files only
- malformed or invalid tokens are rejected when a tool call is made
- changing user-to-group membership should happen in the identity provider, not in this server

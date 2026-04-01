# FastMCP Template Servers

This repository is a small template collection for MCP servers, highlighting different features of MCP servers that can be used with [Erato](https://erato.chat).
Each subdirectory is an independent Python project that uses:

- `uv` for package management
- a local `Justfile` with `just install` and `just run`
- `FastMCP` pinned to the latest PyPI release available when this repository was scaffolded, `3.1.1` (released March 14, 2026)

## Repository Layout

- `api-key-server/`: streamable HTTP MCP server that grants full access when the client sends the configured `X-Api-Key`
- `oidc-id-token-server/`: streamable HTTP MCP server that validates OIDC-style JWT ID tokens and authorizes access from the token's `groups` claim

Both examples expose the same tool surface:

- `list_files`: list the baked-in demo files currently visible to the caller
- `get_file`: read a single baked-in demo file by name

Each project ships with about ten small dummy files in code so the authentication mode changes what the user can see without depending on external storage.

## Common Workflow

From any project directory:

```bash
just install
just run
```

Both projects default to FastMCP's streamable HTTP transport and are meant to be connected from Erato using an `erato.toml` entry similar to the examples in each project README.

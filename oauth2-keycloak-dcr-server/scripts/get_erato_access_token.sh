#!/bin/sh
set -eu

KEYCLOAK_BASE_URL="${KEYCLOAK_BASE_URL:-http://127.0.0.1:8080}"
KEYCLOAK_REALM="${KEYCLOAK_REALM:-mcp-demo}"
ERATO_CLIENT_ID="${ERATO_CLIENT_ID:-erato-local-dev}"
DEMO_USERNAME="${DEMO_USERNAME:-erato-demo}"
DEMO_PASSWORD="${DEMO_PASSWORD:-erato-demo-password}"
MCP_SCOPE="${MCP_SCOPE:-openid mcp:tools mcp:admin}"

token_response="$(
  curl -fsS \
    -X POST \
    "${KEYCLOAK_BASE_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "grant_type=password" \
    --data-urlencode "client_id=${ERATO_CLIENT_ID}" \
    --data-urlencode "username=${DEMO_USERNAME}" \
    --data-urlencode "password=${DEMO_PASSWORD}" \
    --data-urlencode "scope=${MCP_SCOPE}"
)"

printf '%s\n' "${token_response}" | python3 -c '
import json, sys
payload = json.load(sys.stdin)
print(payload["access_token"])
'

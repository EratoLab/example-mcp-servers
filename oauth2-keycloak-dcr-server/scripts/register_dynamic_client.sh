#!/bin/sh
set -eu

CLIENT_ID="${1:-demo-dcr-client}"
COMPOSE_PROJECT_DIR="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"

KEYCLOAK_REALM="${KEYCLOAK_REALM:-mcp-demo}"
KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:8080}"
KEYCLOAK_ADMIN_USERNAME="${KEYCLOAK_ADMIN_USERNAME:-admin}"
KEYCLOAK_ADMIN_PASSWORD="${KEYCLOAK_ADMIN_PASSWORD:-admin}"
MCP_TOOLS_SCOPE="${MCP_TOOLS_SCOPE:-mcp:tools}"
MCP_ADMIN_SCOPE="${MCP_ADMIN_SCOPE:-mcp:admin}"

docker compose -f "${COMPOSE_PROJECT_DIR}/docker-compose.yml" exec -T keycloak /bin/sh <<EOF
set -eu
/opt/keycloak/bin/kcreg.sh config credentials \
  --server "${KEYCLOAK_URL}" \
  --realm master \
  --user "${KEYCLOAK_ADMIN_USERNAME}" \
  --password "${KEYCLOAK_ADMIN_PASSWORD}"

/opt/keycloak/bin/kcreg.sh create \
  -r "${KEYCLOAK_REALM}" \
  -s clientId="${CLIENT_ID}" \
  -s publicClient=true \
  -s 'redirectUris=["http://127.0.0.1/*","http://localhost/*"]' \
  -s 'webOrigins=["http://127.0.0.1:*","http://localhost:*"]' \
  -s 'grantTypes=["authorization_code","refresh_token"]' \
  -s 'responseTypes=["code"]' \
  -s 'scope="openid ${MCP_TOOLS_SCOPE} ${MCP_ADMIN_SCOPE}"'
EOF

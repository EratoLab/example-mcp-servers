#!/bin/sh
set -eu

KEYCLOAK_URL="${KEYCLOAK_URL:-http://keycloak:8080}"
REALM="${KEYCLOAK_REALM:-mcp-demo}"
ADMIN_USERNAME="${KEYCLOAK_ADMIN_USERNAME:-admin}"
ADMIN_PASSWORD="${KEYCLOAK_ADMIN_PASSWORD:-admin}"
MCP_RESOURCE_URL="${MCP_RESOURCE_URL:-http://127.0.0.1:8003/mcp}"
DEMO_USERNAME="${DEMO_USERNAME:-erato-demo}"
DEMO_EMAIL="${DEMO_EMAIL:-erato-demo@example.com}"
DEMO_PASSWORD="${DEMO_PASSWORD:-erato-demo-password}"
ERATO_CLIENT_ID="${ERATO_CLIENT_ID:-erato-local-dev}"
MCP_TOOLS_SCOPE="${MCP_TOOLS_SCOPE:-mcp:tools}"
MCP_ADMIN_SCOPE="${MCP_ADMIN_SCOPE:-mcp:admin}"

KCADM="/opt/keycloak/bin/kcadm.sh"

wait_for_keycloak() {
  until curl -fsS "${KEYCLOAK_URL}/realms/master/.well-known/openid-configuration" >/dev/null 2>&1; do
    sleep 2
  done
}

get_first_id() {
  sed -n 's/.*"id" *: *"\([^"]*\)".*/\1/p' | head -n 1
}

ensure_realm() {
  if ! "${KCADM}" get "realms/${REALM}" >/dev/null 2>&1; then
    "${KCADM}" create realms \
      -s realm="${REALM}" \
      -s enabled=true \
      -s loginWithEmailAllowed=true \
      -s duplicateEmailsAllowed=false \
      -s registrationAllowed=false
  fi
}

ensure_user() {
  "${KCADM}" create users -r "${REALM}" \
    -s username="${DEMO_USERNAME}" \
    -s enabled=true \
    -s email="${DEMO_EMAIL}" \
    -s emailVerified=true \
    >/dev/null 2>&1 || true

  "${KCADM}" set-password -r "${REALM}" \
    --username "${DEMO_USERNAME}" \
    --new-password "${DEMO_PASSWORD}"
}

ensure_scope() {
  scope_name="$1"

  "${KCADM}" create client-scopes -r "${REALM}" \
    -s name="${scope_name}" \
    -s protocol=openid-connect \
    -s attributes.'include.in.token.scope'=true \
    >/dev/null 2>&1 || true

  scope_id="$("${KCADM}" get client-scopes -r "${REALM}" -q name="${scope_name}" | get_first_id)"
  if [ -z "${scope_id}" ]; then
    echo "Unable to locate client scope ${scope_name}" >&2
    exit 1
  fi

  "${KCADM}" create "client-scopes/${scope_id}/protocol-mappers/models" -r "${REALM}" \
    -s name="${scope_name}-audience" \
    -s protocol=openid-connect \
    -s protocolMapper=oidc-audience-mapper \
    -s config.'included.custom.audience'="${MCP_RESOURCE_URL}" \
    -s config.'access.token.claim'=true \
    -s config.'id.token.claim'=false \
    >/dev/null 2>&1 || true
}

ensure_erato_client() {
  "${KCADM}" create clients -r "${REALM}" \
    -s clientId="${ERATO_CLIENT_ID}" \
    -s enabled=true \
    -s publicClient=true \
    -s directAccessGrantsEnabled=true \
    -s standardFlowEnabled=true \
    -s 'redirectUris=["http://127.0.0.1/*","http://localhost/*"]' \
    -s 'webOrigins=["http://127.0.0.1:*","http://localhost:*"]' \
    -s "optionalClientScopes=[\"profile\",\"email\",\"roles\",\"web-origins\",\"acr\",\"${MCP_TOOLS_SCOPE}\",\"${MCP_ADMIN_SCOPE}\"]" \
    >/dev/null 2>&1 || true
}

wait_for_keycloak

"${KCADM}" config credentials \
  --server "${KEYCLOAK_URL}" \
  --realm master \
  --user "${ADMIN_USERNAME}" \
  --password "${ADMIN_PASSWORD}"

ensure_realm
ensure_user
ensure_scope "${MCP_TOOLS_SCOPE}"
ensure_scope "${MCP_ADMIN_SCOPE}"
ensure_erato_client

echo "Keycloak bootstrap finished for realm ${REALM}."

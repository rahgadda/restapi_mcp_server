#!/usr/bin/env bash
set -euo pipefail

# Usage: create_billing_account.sh <session> [restapi_url]
# - session (required): orchestrator session identifier to inject into the request template.
# - restapi_url (optional): override orchestrator endpoint.
#   Defaults to $RESTAPI_URL or http://100.76.169.105:9090/api/v001/restapi/call

SESSION="${1:-${SESSION:-}}"
if [[ -z "$SESSION" ]]; then
  echo "Usage: $0 <session> [restapi_url]" >&2
  exit 1
fi

RESTAPI_URL="${2:-${RESTAPI_URL:-http://100.76.169.105:9090/api/v001/restapi/call}}"

# Resolve the template relative to this script's directory for robust invocation
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null 2>&1 && pwd)"
TEMPLATE_JSON="${SCRIPT_DIR}/create_billing_account.template.json"

if [[ ! -f "$TEMPLATE_JSON" ]]; then
  echo "Template JSON not found: $TEMPLATE_JSON" >&2
  exit 1
fi

echo "Rendering request from template ${TEMPLATE_JSON}" >&2
REQ_FILE="${TMPDIR:-/tmp}/create_billing_account.$$.json"
# Inject the provided session into the template before making the call.
escaped_session="$(printf '%s' "$SESSION" | sed -e 's/[\\/&]/\\&/g')"
sed "s/__SESSION__/${escaped_session}/g" "$TEMPLATE_JSON" >"$REQ_FILE"
echo "Request written to $REQ_FILE" >&2

echo "Posting CREATE-BILLING-ACCOUNT to ${RESTAPI_URL}" >&2
RESP_FILE="${TMPDIR:-/tmp}/create_billing_account.response.$$.json"
HTTP_CODE=$(curl -sS -X POST "${RESTAPI_URL}" -H 'Content-Type: application/json' -d @"$REQ_FILE" -o "$RESP_FILE" -w '%{http_code}' || echo 000)

echo "Response:" >&2
if command -v jq >/dev/null 2>&1; then
  jq . "$RESP_FILE" 2>/dev/null || cat "$RESP_FILE"
else
  cat "$RESP_FILE"
fi

# Prefer JSON-provided response_status if present; else fallback to curl HTTP code
json_code=$(jq -r '.response_status // empty' "$RESP_FILE" 2>/dev/null | sed -E 's/[^0-9]*([0-9]{3}).*/\1/' || true)

effective_code="$json_code"
if [[ -z "$effective_code" || ! "$effective_code" =~ ^[0-9]{3}$ ]]; then
  effective_code="$HTTP_CODE"
fi

if [[ -z "$effective_code" || ! "$effective_code" =~ ^[0-9]{3}$ ]]; then
  echo "Unable to determine status code; treating as failure" >&2
  exit 1
fi

if (( effective_code < 200 || effective_code >= 300 )); then
  echo "Non-2xx status detected: $effective_code" >&2
  exit 1
fi

echo "Done." >&2


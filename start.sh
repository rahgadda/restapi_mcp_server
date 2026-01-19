#!/usr/bin/env bash
# Start script to pull and run the published image if not present.
# Defaults to ghcr.io/rahgadda/restapi_mcp_server:0.0.1 and mirrors install.sh
# behavior for proxy env, storage/logs mapping, ports, and log following.
#
# Usage:
#   ./start.sh                 # pull if missing, run detached, follow logs
#   ./start.sh --no-proxy      # do not set proxy env vars
#   ./start.sh --docker-attach # run in foreground
#   ./start.sh --no-follow     # do not follow logs after starting
#   ./start.sh --docker-tag=ghcr.io/rahgadda/restapi_mcp_server:0.0.1
#   ./start.sh --docker-name=restapi-mcp-server
#
# Optional env overrides:
#   IMAGE_TAG, CONTAINER_NAME, HOST_STORAGE_DIR, LOG_DIR, DEBUG, LOG_LEVEL

set -euo pipefail

# -----------------------------
# Defaults / Args
# -----------------------------
USE_PROXY=1
DOCKER_DETACH=1
FOLLOW_LOGS=1
DOCKER_TAG="${IMAGE_TAG:-ghcr.io/rahgadda/restapi_mcp_server:0.0.1}"
DOCKER_NAME="${CONTAINER_NAME:-restapi-mcp-server}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST_STORAGE_DIR="${HOST_STORAGE_DIR:-${PROJECT_ROOT}/storage}"
LOG_DIR="${LOG_DIR:-${PROJECT_ROOT}/logs}"
LOG_FILE="${LOG_DIR}/docker.log"

mkdir -p "${HOST_STORAGE_DIR}" "${LOG_DIR}"
: > "${LOG_FILE}"

for arg in "$@"; do
  case "$arg" in
    --no-proxy) USE_PROXY=0 ;;
    --docker-attach) DOCKER_DETACH=0 ;;
    --no-follow) FOLLOW_LOGS=0 ;;
    --docker-tag=*) DOCKER_TAG="${arg#*=}" ;;
    --docker-name=*) DOCKER_NAME="${arg#*=}" ;;
    *) echo "Unknown arg: $arg" >&2; exit 1 ;;
  esac
done

# -----------------------------
# Optional proxy configuration (same defaults as install.sh)
# -----------------------------
if [[ "${USE_PROXY}" -eq 1 ]]; then
  http_proxy=${http_proxy:-http://rmdc-proxy.oracle.com:80/}
  https_proxy=${https_proxy:-http://rmdc-proxy.oracle.com:80/}
  no_proxy=${no_proxy:-localhost,.oraclecorp.com,.svc.cluster.local,127.0.0.1,.in.oracle.com,.oraclevcn.com,.local,.ocs.oc-test.com}
  export http_proxy https_proxy no_proxy
  export HTTP_PROXY="${HTTP_PROXY:-$http_proxy}"
  export HTTPS_PROXY="${HTTPS_PROXY:-$https_proxy}"
  export NO_PROXY="${NO_PROXY:-$no_proxy}"
else
  unset http_proxy https_proxy no_proxy HTTP_PROXY HTTPS_PROXY NO_PROXY || true
fi

# -----------------------------
# Ensure required host files/folders exist (CSV skeletons)
# -----------------------------
STORAGE_DIR="${HOST_STORAGE_DIR}"
ENV_CSV="${STORAGE_DIR}/environment.csv"
TXN_CSV="${STORAGE_DIR}/transaction.csv"
mkdir -p "${STORAGE_DIR}"

if [[ ! -f "${ENV_CSV}" ]]; then
  echo "environment,variable,value" > "${ENV_CSV}"
  echo "[init] Created ${ENV_CSV}"
fi

if [[ ! -f "${TXN_CSV}" ]]; then
  cat > "${TXN_CSV}" <<'CSV'
transactionId,session,action,http_method,request,response,status,creation_dt,last_updation_dt
CSV
  echo "[init] Created ${TXN_CSV}"
fi

# -----------------------------
# Prereqs
# -----------------------------
if ! command -v docker >/dev/null 2>&1; then
  echo "[docker] docker CLI not found. Please install Docker." >&2
  exit 1
fi

# -----------------------------
# Pull image if missing (no build here)
# -----------------------------
if [[ -z "$(docker images -q "${DOCKER_TAG}" 2>/dev/null)" ]]; then
  echo "[docker] Image ${DOCKER_TAG} not found locally. Pulling..."
  if ! docker pull "${DOCKER_TAG}" 2>&1 | tee -a "${LOG_FILE}"; then
    echo "[docker] Failed to pull ${DOCKER_TAG}. If this is private, ensure Docker is logged in to ghcr.io." >&2
    echo "        Login: echo <TOKEN> | docker login ghcr.io -u <USERNAME> --password-stdin" >&2
    exit 1
  fi
else
  echo "[docker] Image ${DOCKER_TAG} already present locally."
fi

# -----------------------------
# Run container
# -----------------------------
# Stop and remove existing container if present
(docker rm -f "${DOCKER_NAME}" >/dev/null 2>&1) || true

# Build docker env args (proxied if set in environment)
DOCKER_ENV=( )
for var in http_proxy https_proxy no_proxy HTTP_PROXY HTTPS_PROXY NO_PROXY DEBUG LOG_LEVEL; do
  if [[ -n "${!var-}" ]]; then
    DOCKER_ENV+=( -e "$var=${!var}" )
  fi
done

DOCKER_RUN_BASE=(
  docker run
  --name "${DOCKER_NAME}"
  -p 9090:9090
  -p 8765:8765
  -v "${HOST_STORAGE_DIR}:/app/storage"
  -v "${LOG_DIR}:/app/logs"
  "${DOCKER_ENV[@]}"
)

if [[ "${DOCKER_DETACH}" -eq 1 ]]; then
  echo "[docker] Starting container in background..."
  "${DOCKER_RUN_BASE[@]}" -d "${DOCKER_TAG}" >/dev/null
  echo "[docker] Container: ${DOCKER_NAME}  Image: ${DOCKER_TAG}"
  echo "[docker] Ports: 9090 (API), 8765 (MCP SSE)"
  if [[ "${FOLLOW_LOGS}" -eq 1 ]]; then
    echo "[docker] Following logs (Ctrl+C to stop following; container continues running). Mirroring to ${LOG_FILE}"
    docker logs -f "${DOCKER_NAME}" | tee -a "${LOG_FILE}"
  fi
else
  echo "[docker] Running container in foreground... (Ctrl+C to stop). Mirroring to ${LOG_FILE}"
  "${DOCKER_RUN_BASE[@]}" --rm "${DOCKER_TAG}" | tee -a "${LOG_FILE}"
fi

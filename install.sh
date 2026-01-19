#!/bin/bash

# UV Env
source $HOME/.local/bin/env

# Proxy Setting
http_proxy=${http_proxy:-http://rmdc-proxy.oracle.com:80/}
https_proxy=${https_proxy:-http://rmdc-proxy.oracle.com:80/}
no_proxy=${no_proxy:-localhost,.oraclecorp.com,.svc.cluster.local,127.0.0.1,.in.oracle.com,.oraclevcn.com,.local,.ocs.oc-test.com}
export http_proxy https_proxy no_proxy
export HTTP_PROXY="${HTTP_PROXY:-$http_proxy}"
export HTTPS_PROXY="${HTTPS_PROXY:-$https_proxy}"
export NO_PROXY="${NO_PROXY:-$no_proxy}"

# Load Python Virtual Environment
source /scratch/automation/.venv/bin/activate

# Allow Firewall
sudo firewall-cmd --zone=public --permanent --add-port=9090/tcp
sudo firewall-cmd --zone=public --permanent --add-port=8765/tcp
sudo firewall-cmd --reload 

# Docker Build
docker build -f Docker --build-arg "http_proxy=${http_proxy:-}" --build-arg "https_proxy=${https_proxy:-}" --build-arg "no_proxy=${no_proxy:-}" --build-arg "HTTP_PROXY=${HTTP_PROXY:-}" --build-arg "HTTPS_PROXY=${HTTPS_PROXY:-}" --build-arg "NO_PROXY=${NO_PROXY:-}" -t ghcr.io/rahgadda/restapi_mcp_server:0.0.1 .
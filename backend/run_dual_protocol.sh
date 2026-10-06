#!/usr/bin/env bash
set -Eeuo pipefail

CERT_FILE="${TLS_CERTFILE:-/certs/localhost.pem}"
KEY_FILE="${TLS_KEYFILE:-/certs/localhost-key.pem}"
if [[ ! -r "$CERT_FILE" || ! -r "$KEY_FILE" ]]; then
  echo "Local TLS certificate is missing. Generate it with mkcert as documented in docs/backend-verification.md." >&2
  exit 1
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
HTTP_PID=$!
uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-certfile "$CERT_FILE" --ssl-keyfile "$KEY_FILE" &
TLS_PID=$!
cleanup() {
  kill "$HTTP_PID" "$TLS_PID" 2>/dev/null || true
  wait "$HTTP_PID" "$TLS_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
wait -n "$HTTP_PID" "$TLS_PID"

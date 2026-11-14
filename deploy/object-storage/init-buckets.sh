#!/usr/bin/env bash
# Idempotent MinIO Object Storage Bucket Initialization aligned with PlatformConfig
set -euo pipefail

MINIO_ALIAS="${MINIO_ALIAS:-fmdp}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://minio:9000}"
MINIO_ROOT_USER="${MINIO_ROOT_USER:?MINIO_ROOT_USER is required}"
MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:?MINIO_ROOT_PASSWORD is required}"

mc alias set "$MINIO_ALIAS" "$MINIO_ENDPOINT" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

for bucket in lakehouse-bronze lakehouse-silver lakehouse-gold lakehouse-checkpoints; do
  mc mb --ignore-existing "${MINIO_ALIAS}/${bucket}"
done


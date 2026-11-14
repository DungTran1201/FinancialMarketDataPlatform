#!/usr/bin/env bash
# Declarative Kafka Topic Bootstrap Script aligned with models/data-platform/topics.yaml
set -euo pipefail

BOOTSTRAP="${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092}"

create_topic() {
  local topic="$1"
  local partitions="$2"
  local retention_ms="$3"
  kafka-topics.sh --bootstrap-server "$BOOTSTRAP" \
    --create --if-not-exists \
    --topic "$topic" \
    --partitions "$partitions" \
    --replication-factor 1 \
    --config "retention.ms=$retention_ms" \
    --config "cleanup.policy=delete"
}

# Canonical Data Plane Event Topics (7 days = 604800000 ms; 30 days = 2592000000 ms)
create_topic "market.raw.trades.v1"     6 604800000
create_topic "market.raw.klines.v1"     6 604800000
create_topic "market.raw.tickers.v1"    6 604800000
create_topic "market.raw.orderbook.v1"  6 604800000
create_topic "market.anomalies.v1"      3 2592000000
create_topic "market.dlq.v1"            3 2592000000

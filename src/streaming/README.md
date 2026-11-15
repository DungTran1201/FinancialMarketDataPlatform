# Streaming Subsystem (`src/streaming/`)

Owns **Stage 4** (partitioned Kafka event streaming & DLQ routing) and real-time streaming consumers projecting Kafka topics into low-latency operational stores and anomaly streams.

## Subpackages

| Directory | Responsibility | Scope |
|---|---|---|
| `contracts/` | Consumer group identifiers (`CG_*`), canonical topic registry (`ALL_CANONICAL_TOPICS`), and `StreamBrokerPort` Protocol | Decouples producers and sinks from Kafka internals. |
| `infrastructure/` | `ConfluentKafkaStreamingAdapter` (`acks=all`, idempotent producer, manual commit) and `PartitionedEventStreamingBroker` (6-partition symbol hashing + offset tracking) | Transport & broker mechanics only. |
| `consumers/` | Real-time stream processors: `hot_redis.py` (Lua monotonic state projector), `analytics_ch.py` (micro-batch ClickHouse sink), `anomaly_detector.py` (Z-score with 15-min cooldown) | Commits Kafka offsets **only after** sink projection succeeds. |


"""Contract Verification for Kafka Topic Routing & Shared Canonical Dataset Schemas (`TC-014`)."""

from __future__ import annotations

import unittest

from src.shared.contracts.events.market_events import KafkaTopic
from src.shared.contracts.schemas.datasets import CANONICAL_DATASET_CONTRACTS, DatasetLayer
from src.streaming.contracts.topics import (
    ALL_CANONICAL_TOPICS,
    CG_ANALYTICS_CH,
    CG_ANOMALY_DETECTOR,
    CG_HOT_REDIS,
    CG_LAKEHOUSE_BRONZE,
)


class TestDataPlatformSchemaAndTopicContracts(unittest.TestCase):
    """Ensures canonical Kafka topic names, consumer groups, and dataset keys stay synchronized."""

    def test_all_six_canonical_kafka_topics_and_consumer_groups_are_registered(self) -> None:
        self.assertEqual(len(ALL_CANONICAL_TOPICS), 6)
        self.assertIn(KafkaTopic.TRADES_V1, ALL_CANONICAL_TOPICS)
        self.assertIn(KafkaTopic.DLQ_V1, ALL_CANONICAL_TOPICS)
        self.assertEqual(len({CG_HOT_REDIS, CG_ANALYTICS_CH, CG_LAKEHOUSE_BRONZE, CG_ANOMALY_DETECTOR}), 4)

    def test_silver_and_gold_dataset_contracts_define_natural_keys(self) -> None:
        self.assertIn("silver.market_klines", CANONICAL_DATASET_CONTRACTS)
        self.assertIn("gold.fct_daily_market_summary", CANONICAL_DATASET_CONTRACTS)
        for name, contract in CANONICAL_DATASET_CONTRACTS.items():
            self.assertGreater(len(contract.natural_key), 0, f"{name} must specify natural_key")
            self.assertIn(contract.layer, {DatasetLayer.SILVER, DatasetLayer.GOLD})

# [Cell 2.1] File độc lập: Worker chuyên bắt WebSocket của Binance
import asyncio
import json
import time
from datetime import datetime, timezone
import websockets
from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'localhost:9092', 'client.id': 'binance-worker'})
TOPIC = "raw.binance.trades"

async def run():
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    while True:
        try:
            async with websockets.connect(url) as ws:
                async for msg in ws:
                    payload = json.dumps({
                        "metadata": {
                            "source": "binance",
                            "ingested_at": datetime.now(timezone.utc).isoformat()
                        },
                        "raw_payload": json.loads(msg)
                    })
                    producer.produce(TOPIC, key="BTCUSDT", value=payload)
                    producer.poll(0)
        except Exception as e:
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run())

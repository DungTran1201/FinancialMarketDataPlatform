# [Cell 2.2] File độc lập: Worker chuyên bắt WebSocket của Coinbase
import asyncio
import json
from datetime import datetime, timezone
import websockets
from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'localhost:9092', 'client.id': 'coinbase-worker'})
TOPIC = "raw.coinbase.trades"

async def run():
    url = "wss://ws-feed.exchange.coinbase.com"
    sub_msg = json.dumps({"type": "subscribe", "product_ids": ["BTC-USD"], "channels": ["matches"]})
    while True:
        try:
            async with websockets.connect(url) as ws:
                await ws.send(sub_msg)
                async for msg in ws:
                    data = json.loads(msg)
                    if data.get("type") in ["match", "last_match"]:
                        payload = json.dumps({
                            "metadata": {
                                "source": "coinbase",
                                "ingested_at": datetime.now(timezone.utc).isoformat()
                            },
                            "raw_payload": data
                        })
                        producer.produce(TOPIC, key="BTC-USD", value=payload)
                        producer.poll(0)
        except Exception as e:
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run())

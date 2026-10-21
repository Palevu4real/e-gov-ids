import asyncio
import json
import logging
import sys

from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.alert import Alert

# --- Logging setup -----------------------------------------------------------
# Uvicorn only configures its own loggers, so our logger would inherit the root
# default level (WARNING) and silently drop log.info(). Configure it explicitly.
log = logging.getLogger("kafka-consumer")
log.setLevel(logging.INFO)
if not log.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(
        logging.Formatter("%(levelname)s:     [%(name)s] %(message)s")
    )
    log.addHandler(_handler)
    log.propagate = False  # avoid duplicate lines if root logger is configured

print("🚀 KAFKA CONSUMER FILE LOADED", flush=True)

GROUP_ID = "ids-backend-fresh-1"
MAX_ATTEMPTS = 10
START_TIMEOUT = 15  # seconds to wait for consumer.start() before giving up on an attempt


async def consume_alerts():
    """Background task that listens to Kafka and saves alerts to Postgres."""
    print("▶️ consume_alerts() task started", flush=True)

    # Give Kafka a moment to come up
    await asyncio.sleep(5)

    print(
        f"🔌 Connecting to Kafka at {settings.KAFKA_BOOTSTRAP_SERVERS}, "
        f"topic={settings.KAFKA_TOPIC_DETECTIONS}, group={GROUP_ID}",
        flush=True,
    )

    # Retry connecting until Kafka is actually ready.
    # A fresh consumer is created per attempt because a half-started one can't be reused.
    consumer = None
    started = False
    for attempt in range(1, MAX_ATTEMPTS + 1):
        consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_DETECTIONS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=GROUP_ID,
            auto_offset_reset="earliest",
        )
        try:
            # wait_for turns a silent hang into a visible TimeoutError
            await asyncio.wait_for(consumer.start(), timeout=START_TIMEOUT)
            started = True
            break
        except asyncio.CancelledError:
            try:
                await consumer.stop()
            except Exception:
                pass
            raise
        except Exception as e:  # includes asyncio.TimeoutError
            msg = f"Kafka Consumer Startup Error (attempt {attempt}/{MAX_ATTEMPTS}): {e!r}"
            log.error(msg)
            print(f"❌ {msg}", flush=True)
            try:
                await consumer.stop()
            except Exception:
                pass
            await asyncio.sleep(5)

    if not started:
        log.error(f"❌ Could not connect to Kafka after {MAX_ATTEMPTS} attempts. Giving up.")
        print(f"❌ Could not connect to Kafka after {MAX_ATTEMPTS} attempts. Giving up.", flush=True)
        return

    log.info("✅ Kafka Consumer started. Listening for alerts...")
    print("✅ Kafka Consumer started", flush=True)
    print(f"📌 Assigned partitions: {consumer.assignment()}", flush=True)

    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))
                log.warning(f"📥 Received alert from Kafka: {data.get('alert_type')}")

                async with AsyncSessionLocal() as db:
                    new_alert = Alert(
                        severity=data.get("severity", "medium"),
                        alert_type=data.get("alert_type", "unknown"),
                        source_ip=data.get("source_ip"),
                        dest_ip=data.get("dest_ip"),
                        details=data,
                    )
                    db.add(new_alert)
                    await db.commit()
                    log.warning(
                        f"💾 Saved alert to DB: {data.get('alert_type')} "
                        f"from {data.get('source_ip')}"
                    )
            except Exception as e:
                log.error(f"Failed to process message: {e!r}")

    except asyncio.CancelledError:
        log.info("Kafka consumer task cancelled, shutting down...")
        raise
    except Exception as e:
        log.error(f"Kafka Consumer Runtime Error: {e!r}")
    finally:
        await consumer.stop()
        log.info("Kafka consumer stopped.")
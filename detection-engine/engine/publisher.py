import json
import logging
from aiokafka import AIOKafkaProducer
import os

log = logging.getLogger("detection-engine")

class KafkaPublisher:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
        self.topic = os.getenv("KAFKA_TOPIC_DETECTIONS", "ids.detections")
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        log.info("Kafka Producer started.")

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def publish(self, alert_data):
        if self.producer:
            await self.producer.send_and_wait(self.topic, alert_data)
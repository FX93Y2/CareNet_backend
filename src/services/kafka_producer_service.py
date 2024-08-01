import json
from src.utils.kafka_config import get_kafka_producer
from src.utils.error_handling import AppException

class KafkaProducerService:
    def __init__(self):
        self.producer = None

    async def initialize(self):
        self.producer = await anext(get_kafka_producer())

    async def publish_message(self, topic: str, message: dict):
        if not self.producer:
            raise AppException(status_code=500, detail="Kafka producer not initialized")
        try:
            value = json.dumps(message).encode('utf-8')
            await self.producer.send_and_wait(topic, value)
        except Exception as e:
            raise AppException(status_code=500, detail=f"Failed to publish message: {str(e)}")

    async def close(self):
        if self.producer:
            await self.producer.stop()
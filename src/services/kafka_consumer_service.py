import json
from src.utils.kafka_config import get_kafka_consumer
from src.utils.error_handling import AppException

class KafkaConsumerService:
    def __init__(self, topic: str):
        self.topic = topic
        self.consumer = None

    async def initialize(self):
        self.consumer = await anext(get_kafka_consumer(self.topic))

    async def consume_messages(self):
        if not self.consumer:
            raise AppException(status_code=500, detail="Kafka consumer not initialized")
        try:
            async for message in self.consumer:
                yield json.loads(message.value.decode('utf-8'))
        except Exception as e:
            raise AppException(status_code=500, detail=f"Failed to consume message: {str(e)}")

    async def close(self):
        if self.consumer:
            await self.consumer.stop()
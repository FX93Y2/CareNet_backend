from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from src.utils.config import Settings

settings = Settings()

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

async def get_kafka_consumer(topic):
    consumer = AIOKafkaConsumer(topic, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    await consumer.start()
    try:
        yield consumer
    finally:
        await consumer.stop()
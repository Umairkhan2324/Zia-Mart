from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from fastapi import Depends
# from app.db_engine import engine
from typing import Annotated

# Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
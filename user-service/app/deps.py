from aiokafka import AIOKafkaProducer
from sqlmodel import Session,select
from fastapi import Depends
from app.db_engine import engine
from typing import Annotated
# Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
GetProducer = Annotated[AIOKafkaProducer,Depends(get_kafka_producer)]
def get_session():
    with Session(engine) as session:
        yield session


DBSessionDep = Annotated[Session,Depends(get_session)]
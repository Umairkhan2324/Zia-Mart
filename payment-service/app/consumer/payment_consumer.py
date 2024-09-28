import asyncio
import json
from uuid import UUID
from aiokafka import AIOKafkaConsumer
from sqlmodel import Session
from typing import AsyncGenerator

from app.crud.payment_crud import create_order_payment
from app.deps import get_session
from app.utils.encode_and_decode import custom_decoder
from app.models.payment_model import Payment

async def payment_consume_messages(topic: str, bootstrap_servers: str, group_id: str):
    """Consume payment messages from Kafka and process them."""
    
    # Initialize Kafka consumer
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        # auto_offset_reset="earliest",  # Uncomment if you want to start consuming from the earliest message
    )
    
    print(f"Listening for messages on topic: {topic}")
    
    # Start Kafka consumer
    await consumer.start()

    try:
        # Asynchronously consume messages from the Kafka topic
        async for message in consumer:
            try:
                # Decode and deserialize the message
                payment_data = json.loads(message.value.decode(), object_hook=custom_decoder)
                print(f"Received payment data: {payment_data}")

                # Insert payment data into the database
                with next(get_session()) as session:
                    print("Saving payment data to the database...")
                    create_order_payment(payment=Payment(**payment_data), session=session)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Handle errors related to JSON decoding or missing fields
                print(f"Error processing message: {e}")

    except Exception as e:
        print(f"Kafka Consumer Error: {e}")

    finally:
        # Ensure the consumer is stopped properly
        await consumer.stop()
        print(f"Stopped consuming messages from topic: {topic}")

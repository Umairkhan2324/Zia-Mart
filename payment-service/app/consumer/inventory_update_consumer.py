import asyncio
import json
from typing import List
from uuid import UUID
from aiokafka import AIOKafkaConsumer

from app.db_engine import engine
from app.models.inventory_model import InventoryItems
from app.crud.inventory_crud import inventory_update
from app.deps import get_session

async def consume_update_messages(topic: str, bootstrap_servers: str, group_id: str):
    """Consume inventory update messages from Kafka and update the database."""
    
    # Create a Kafka consumer
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        # auto_offset_reset="earliest", # Uncomment this to start consuming from the earliest message
    )
    
    print(f"Listening for messages on topic: {topic}")
    
    # Start the consumer
    await consumer.start()
    
    try:
        # Continuously listen for messages from the Kafka topic
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            
            try:
                # Decode the message and parse the JSON data
                order_data = json.loads(message.value.decode())
                print(f"Received Data: {order_data}")
                
                # Extract the item ID and the item details from the message
                item_id = UUID(order_data['id'])
                item_data = order_data['item']
                
                # Update the inventory item in the database
                with next(get_session()) as session:
                    inventory_update(
                        item_id=item_id,
                        item=InventoryItems(**item_data),
                        session=session
                    )
                print(f"Inventory item {item_id} updated successfully.")
            
            except (ValueError, KeyError, TypeError) as e:
                print(f"Error processing message: {e}")
    
    except Exception as e:
        print(f"Kafka Consumer Error: {e}")
    
    finally:
        # Ensure the consumer is stopped after processing
        await consumer.stop()

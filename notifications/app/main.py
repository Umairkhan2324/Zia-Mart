from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator
import asyncio

# Import consumers
from app.consumer.product_consumer import consume_product_messages
from app.consumer.order_consumer import consume_order_messages
from app.consumer.payment_status_consumer import consume_payment_status_message
from app.consumer.order_status_consumer import consume_order_status_messages
from app.consumer.user_registrations_consumer import consume_new_registed_user_messages
from app.consumer.inventory_addeded_consumer import consume_add_inventory_messages

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifespan manager for FastAPI, setting up Kafka consumers for the notification service."""
    print("Starting Notification Service...")

    # Define consumer tasks for each Kafka topic
    consumer_tasks = [
        consume_product_messages(
            topic="add-new-product-events",
            bootstrap_servers='broker:19092',
            group_id="product-event-consumer-group-for-notification"
        ),
        consume_order_messages(
            topic="order-placed-event-notification-send-user",
            bootstrap_servers='broker:19092',
            group_id="order-consumer-group-for-notification"
        ),
        consume_payment_status_message(
            topic="payment-status-event",
            bootstrap_servers='broker:19092',
            group_id="order-payment-status-consumer-group-for-notification"
        ),
        consume_order_status_messages(
            topic="order-status-event",
            bootstrap_servers='broker:19092',
            group_id="order-status-consumer-group-for-notification"
        ),
        consume_new_registed_user_messages(
            topic="user_registrations",
            bootstrap_servers='broker:19092',
            group_id="user_registrations-consumer-group-for-notification"
        ),
        consume_add_inventory_messages(
            topic="product-response-event-to-inventory",
            bootstrap_servers='broker:19092',
            group_id="add-inventory-consumer-group-for-notification"
        ),
    ]

    task_group = asyncio.gather(*consumer_tasks)

    yield

app = FastAPI(
    lifespan=lifespan,
    title="Notification Service Management",
    version="0.0.1",
    root_path="/notification-service"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Notification Service"}

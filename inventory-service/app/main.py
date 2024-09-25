from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import AsyncGenerator, List
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from uuid import UUID

from app import settings
from app.db_engine import engine
from app.models.inventory_model import InventoryItem, InvetoryItemsUpdate
from app.crud.inventory_crud import (
    create_inventory_item,
    get_all_inventories,
    inventory_update,
    delete_inventory_item,
    get_inventory_item
)
from app.deps import get_session, get_kafka_producer, GetUserDep, DbSessionDeps, ProducerDeps, LoginForAccessTokenDeps
from app.consumer.inventory_consumer import consume_messages
from app.consumer.inventory_update_consumer import consume_update_messages
from app.consumer.order_consumer import consume_order_messages
from app.core.encode_and_decode import CustomJSONEncoder


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables...")

    consumer_tasks = [
        consume_messages(
            topic="product-response-event-to-inventory", 
            bootstrap_servers='broker:19092', 
            group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY
        ),
        consume_update_messages(
            topic="update-inventory-event", 
            bootstrap_servers='broker:19092', 
            group_id="inventory-consumer-group-for-update-inventory"
        ),
        consume_order_messages(
            topic="order-event-for-inventory", 
            bootstrap_servers='broker:19092', 
            group_id="inventory-consumer-group-for-order-quantity-verify"
        )
    ]

    task_group = asyncio.gather(*consumer_tasks)

    create_db_and_tables()
    print("\n\n LIFESPAN created!! \n\n")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Inventory Service Management",
    version="0.0.1",
    root_path="/inventory-service"
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Inventory Service"}


@app.post("/auth/login")
async def login(form_data: LoginForAccessTokenDeps):
    try:
        return form_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-inventory/")
async def generate_inventory(
    inventory: InventoryItem, 
    session: DbSessionDeps, 
    producer: ProducerDeps, 
    user: GetUserDep
):
    """Create a new inventory item and send it to Kafka"""
    if user['role'] == 'admin':
        inventory_data = {field: getattr(inventory, field) for field in inventory.dict()}
        inventory_data['user_id'] = user['id']  
        inventory_json = json.dumps(inventory_data, cls=CustomJSONEncoder).encode("utf-8")

        await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, inventory_json)
        
        return inventory
    raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")


@app.patch("/update-inventory/")
async def update_inventory(
    inventory_id: UUID, 
    item: InvetoryItemsUpdate, 
    session: DbSessionDeps, 
    producer: ProducerDeps, 
    user: GetUserDep
):
    """Update an existing inventory item and send update to Kafka"""
    if user['role'] == 'admin':
        try:
            inventory_data = {"id": str(inventory_id), "item": item.dict()}
            inventory_json = json.dumps(inventory_data).encode("utf-8")
            
            await producer.send_and_wait("update-inventory-event", inventory_json)
            return item
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")

@app.delete("/delete-item/")
def delete_item(
    item_id: UUID, 
    session: DbSessionDeps, 
    user: GetUserDep
):
    """Delete a specific inventory item by its ID"""
    if user['role'] == 'admin':
        try:
            return delete_inventory_item(item_id=item_id, session=session)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")


@app.get("/all-inventory/", response_model=List[InventoryItem])
def get_all_inventory(session: DbSessionDeps):
    """Fetch all inventory items from the database"""
    try:
        return get_all_inventories(session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-inventory-item/", response_model=InventoryItem)
def get_inventory_item(
    item_id: UUID, 
    session: DbSessionDeps
):
    """Fetch a specific inventory item by its ID"""
    try:
        return get_inventory_item(item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

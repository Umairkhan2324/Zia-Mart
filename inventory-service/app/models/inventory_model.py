from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime,timedelta,timezone
from typing import List,Optional
import enum
import uuid
from sqlalchemy import text

# Inventory Microservice Models
class InventoryItems(SQLModel,table=True):
    id: uuid.UUID  = Field(default_factory=uuid.uuid4,primary_key=True,nullable=False)
    product_id: int
    variant_id: int | None = None
    quantity: int
    status: str 


class InvetoryItemsUpdate(SQLModel):
    quantity: int|None = None 
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List, Optional
import enum

# Base Address model
class BaseAddress(SQLModel):
    address: str
    city: str
    country: str
    zipcode: int
    phone: str

# Address model with relationships to orders
class Address(BaseAddress, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    orders: List["Order"] = Relationship(back_populates="address")

# Create User Address model
class CreateUserAddress(BaseAddress):
    pass

# Update Address model
class UpdateAddress(SQLModel):
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    zipcode: Optional[int] = None
    phone: Optional[str] = None

# Order Status enum
class OrderStatus(str, enum.Enum):
    pending = "pending"
    process = "process"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"

# Payment Status enum
class PaymentStatus(str, enum.Enum):
    paid = "paid"
    pending = "pending"
    refunded = "refunded"

# Base Order Items model
class BaseOrderItems(SQLModel):
    product_id: int
    price: float
    quantity: int = Field(default=1)

# Order Items model with relationships to orders
class OrderItems(BaseOrderItems, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: UUID = Field(foreign_key='order.id')
    order: "Order" = Relationship(back_populates='order_items')

# Base Order model
class BaseOrder(SQLModel):
    address_id: int = Field(foreign_key="address.id")

# Order model with relationships and timestamps
class Order(BaseOrder, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    customer_id: int
    total_price: float
    status: OrderStatus = Field(default=OrderStatus.pending)
    payment_status: PaymentStatus = Field(default=PaymentStatus.pending)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.now})

    address: Address = Relationship(back_populates="orders")
    order_items: List[OrderItems] = Relationship(back_populates='order')

# Create Order model
class CreateOrder(BaseOrder):
    order_items: List[BaseOrderItems] = BaseOrderItems

# Output model for Order
class OrderOut(SQLModel):
    id: UUID
    customer_id: int
    total_price: float
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    order_items: List[BaseOrderItems] = []
    address: Address

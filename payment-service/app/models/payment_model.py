from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
import enum

# Enum for Payment Status
class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# PaymentMethod model
class PaymentMethod(SQLModel, table=True):
    """Represents a payment method used in a payment transaction."""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    payment_method: str
    payment_token: Optional[str] = None

    payment: 'Payment' = Relationship(back_populates='payment_method')

# Base model for Payment (used in inheritance)
class BasePayment(SQLModel):
    """Base class containing common fields for Payment models."""
    
    order_id: UUID
    amount: float

# Payment model
class Payment(BasePayment, table=True):
    """Represents the payment transaction including status and method."""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    customer_id: int
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    payment_method_id: Optional[UUID] = Field(foreign_key='paymentmethod.id', default=None)
    payment_method: PaymentMethod = Relationship(back_populates='payment')

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# PaymentCreate model for creating payments
class PaymentCreate(BasePayment):
    """Model used for creating a new payment."""
    pass

# PaymentPublic model for returning payment data publicly
class PaymentPublic(BasePayment):
    """Model for public representation of a payment."""
    
    id: UUID
    customer_id: int
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    # Uncomment the lines below if you need to include timestamps in the public API
    # created_at: datetime
    # updated_at: datetime

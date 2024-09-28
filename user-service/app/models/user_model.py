from sqlmodel import SQLModel, Field, Relationship,Column,VARCHAR
from pydantic import EmailStr
from datetime import datetime,timedelta,timezone
import enum
class Role(str,enum.Enum):
    admin = "admin"
    customer = "customer"

class BaseUser(SQLModel):
    user_name: str = Field(index=True,unique=True)
    full_name: str 
    email: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True))
    phone: str 

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role: Role = Field(default=Role.customer)
    phone: str | None = None
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    # rating: list["ProductRating"] = Relationship(back_populates="product")
    # image: str # Multiple | URL Not Media | One to Manu Relationship
    # quantity: int | None = None # Shall it be managed by Inventory Microservice
    # color: str | None = None # One to Manu Relationship
    # rating: float | None = None # One to Manu Relationship
    
class AdminCreate(BaseUser):
    username: str
    password: str 
    role: Role = Field(default=Role.admin)
# class ProductRating(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     product_id: int = Field(foreign_key="product.id")
#     rating: int
#     review: str | None = None
#     product = Relationship(back_populates="rating")
    
    # user_id: int # One to Manu Relationship

class UserPublicWithRole(BaseUser):
    id: int 
    role: Role   

class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    
class UserUpdate(SQLModel):
    email: str | None = None
    full_name: str | None = None 
    phone: str | None = None 
class UserPublic(BaseUser):
    id: int 
    created_at: datetime
    updated_at: datetime

class UserCreate(BaseUser):
    password: str

class Token(SQLModel):
    access_token: str 
    token_type: str = "bearer"
    expires_in: int 

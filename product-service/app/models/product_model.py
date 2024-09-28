from sqlmodel import SQLModel, Field, Relationship
from typing import List
from pydantic import BaseModel

class CategoryCreate(SQLModel):
    category_name : str

class Category(SQLModel,table=True):
    id : int | None = Field(default=None,primary_key=True)
    category_name : str 
    products : List['Product'] = Relationship(back_populates='category')

class BaseProduct(SQLModel):
    name : str 
    description : str 
    price : float 
    brand : str | None = None
    weight : float | None = None
    sku : str | None = None
     
class Product(BaseProduct, table=True):
    id : int | None = Field(default=None, primary_key=True)
    
    category_id : int = Field(foreign_key="category.id")
    category : Category = Relationship(back_populates="products")

class ProductCreate(BaseProduct):
    category : str 
    
class ProductUpdate(SQLModel):
    name : str | None = None
    description : str | None = None
    price : float | None = None
    expiry : str | None = None
    brand : str | None = None
    weight : float | None = None
    category : str | None = None
    sku : str | None = None
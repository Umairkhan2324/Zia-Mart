from sqlmodel import SQLModel, Field, Relationship
from typing import List
from pydantic import BaseModel

class CategoryCreate(SQLModel):
    category_name : str

class Category(SQLModel,table=True):
    id : int | None = Field(default=None,primary_key=True)
    category_name : str 
    products : List['Product'] = Relationship(back_populates='category')

class ProductImages(SQLModel,table=True):
    id : str | None = Field(default=None,primary_key=True)
    image_url : str 
    product_id : int | None = Field(foreign_key='product.id',default=None)
    product: 'Product' = Relationship(back_populates='images')

class BaseProduct(SQLModel):
    name : str 
    description : str 
    price : float 
    brand : str | None = None
    weight : float | None = None
    sku : str | None = None
     
class Product(BaseProduct, table=True):
    id : int | None = Field(default=None, primary_key=True)
    main_image_url : str| None = None
    rating : list["ProductRating"] = Relationship(back_populates="product")
    
    category_id : int = Field(foreign_key="category.id")
    category : Category = Relationship(back_populates="products")

    images : List[ProductImages] = Relationship(back_populates='product')

class ProductWithImages(BaseProduct):
    id : int 
    images : List[ProductImages] = []
    category : Category | None = None

class ProductCreate(BaseProduct):
    category : str 

class ProductRating(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    product_id : int = Field(foreign_key="product.id")
    rating : int
    review : str | None = None
    product : Product = Relationship(back_populates="rating")
    
class ProductUpdate(SQLModel):
    name : str | None = None
    description : str | None = None
    price : float | None = None
    expiry : str | None = None
    brand : str | None = None
    weight : float | None = None
    category : str | None = None
    sku : str | None = None
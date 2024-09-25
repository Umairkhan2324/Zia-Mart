from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.product_model import Product, ProductUpdate

# Add a New Product to the Database
def add_new_product(product_data: Product, session: Session):
    print("Adding Product to Database")
    session.add(product_data)
    session.commit()
    session.refresh(product_data)
    return product_data

# Get All Products from the Database
def get_all_products(session: Session):
    all_products = session.exec(select(Product)).all()
    return all_products

# Get a Product by ID
def get_product_by_id(product_id: int, session: Session):
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Delete Product by ID
def delete_product_by_id(product_id: int, session: Session):
    # Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Delete the Product
    session.delete(product)
    session.commit()
    return {"message": "Product Deleted Successfully"}
def category_by_name(category_name:str,session:Session):
    category = session.exec(select(Category).where(Category.category_name==category_name)).one_or_none()
    if category is not None:
        return category 
    else: 
        add_new_category = Category(category_name=category_name)
        session.add(add_new_category)
        session.commit()
        session.refresh(add_new_category)
        return add_new_category
    
def category_by_id(category_id:int,session:Session):
    category = session.exec(select(Category).where(Category.id==category_id)).one_or_none()
    if not category:

        raise HTTPException(status_code=404, detail="Category not found")
    
    return category
    
def all_category(session:Session):
    categories = session.exec(select(Category)).all()
    return categories 

def category_delete_by_id(category_id:int,session:Session):
    category = session.exec(select(Category).where(Category.id==category_id)).one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"message":"Category Deleted Successfully"}
        
# Validate Product by ID
def validate_product_by_id(product_id: int, session: Session) -> Product | None:
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    return product    
 
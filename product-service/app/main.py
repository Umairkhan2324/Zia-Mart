# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException,File,UploadFile
from typing import AsyncGenerator,List
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.product_model import Product, ProductUpdate,ProductCreate,ProductImages,ProductWithImages,Category,CategoryCreate
from app.crud.product_crud import add_new_product, get_all_products, get_product_by_id, delete_product_by_id, update_product_by_id,upload_product_image,category_by_name,all_category,category_by_id,category_delete_by_id
from app.deps import get_session, get_kafka_producer,LoginForAccessTokenDeps,CurrentUserDeps,DbSessionDeps,GetProducerDeps

from app.consumer.product_consumer import consume_product_messages
from app.consumer.inventory_consumer import consume_inventory_messages
from app.consumer.order_consumer import consumer_order_messages

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)





# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating table...")


    consumer_tasks = [
        consume_inventory_messages(
            "verification-inventory-events", 'broker:19092',"inventory-consumer-group-for-product-validation"),
        consumer_order_messages(
            "order-events-for-product-verify", 'broker:19092',"order-consumer-group-for-product-verify")]
    task_group = asyncio.gather(*consumer_tasks)
    create_db_and_tables()
    
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Product Service Management",
    version="0.0.1",
    root_path="/product-service"
)



@app.get("/")
def read_root():
    return {"Hello": "Product Service"}


@app.post("/manage-products/")
async def create_new_product(
    session: DbSessionDeps, 
    producer: GetProducerDeps,
    user:CurrentUserDeps,
    product: ProductCreate = Depends(), 
    files:List[UploadFile]=File(...)
    
    ):

    """ Create a new product and send it to Kafka"""
    if user['role'] == "admin":
        
        product_data = await add_new_product(product_data=product,files=files,session=session)
        product_dict = {field: getattr(product_data, field) for field in product_data.dict()}

        product_dict['user_id'] = user['id']
        product_json = json.dumps(product_dict).encode("utf-8")
        print("product_JSON:", product_json)
        # # print(f"file data {file_data.json()}")
        # # Produce message
        await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC,product_json)
        
        return product_data
    else:
        raise HTTPException(status_code=403,detail="The user doesn't have enough privileges")

@app.post("/auth/login")
async def login(form_data:LoginForAccessTokenDeps):
    try:
        return form_data
    except Exception as e:
        return e 


@app.get("/get-all-products", response_model=list[ProductWithImages])
def all_products(session: DbSessionDeps):
    """ Get all products from the database"""
    return get_all_products(session)

@app.get("/get-product/{product_id}", response_model=ProductWithImages)
def get_single_product(product_id: int, session: DbSessionDeps):
    """ Get a single product by ID"""
    try:
        return get_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/manage-products/{product_id}", response_model=dict)
def delete_single_product(product_id: int, session:DbSessionDeps,user:CurrentUserDeps):
    """ Delete a single product by ID"""
    
    if user['role'] == 'admin':
        try:
            return delete_product_by_id(product_id=product_id, session=session)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    raise HTTPException(status_code=403,detail="The user doesn't have enough privileges")
    
@app.patch("/manage-products/{product_id}", response_model=Product)
def update_single_product(product_id: int, product: ProductUpdate, session:DbSessionDeps, user:CurrentUserDeps):
    """ Update a single product by ID"""
    if user['role'] == 'admin':
        
        try:
            return update_product_by_id(product_id=product_id, to_update_product_data=product, session=session)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    raise HTTPException(status_code=403,detail="The user doesn't have enough privileges")    
        
    
@app.post("/upload-product-image/{product_id}")
async def product_image_upload(product_id:int,session:DbSessionDeps, user:CurrentUserDeps,product_image:UploadFile=File(...)):
    if user['role'] == 'admin':
        try:
            print(product_image)
            return await upload_product_image(product_id=product_id,product_image=product_image, session=session)
            # return "image upload success fully"
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    raise HTTPException(status_code=403,detail="The user doesn't have enough privileges")    


@app.post("/create-category/", response_model=Category)
async def category_create(category:CategoryCreate,session:DbSessionDeps, user:CurrentUserDeps):
    if user['role'] == "admin":
        try:
            return category_by_name(category_name=category.category_name,session=session)
        except HTTPException as e:
            raise e 
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-category/{category_id}", response_model=Category)
async def category_get(category_id:int,session:DbSessionDeps):
    try:
        return category_by_id(category_id=category_id,session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-all-categories", response_model=list[Category])
async def category_get_all(session:DbSessionDeps):
    try:
        return all_category(session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/detele-category/{category_id}",response_model=dict)
def category_delete(category_id:int,session:DbSessionDeps,user:CurrentUserDeps):
    if user['role'] == "admin":
        try:
            return category_delete_by_id(category_id=category_id,session=session)
        except HTTPException as e:
            raise e 
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))





# @app.get("/user/me")
# async def user_me(user:CurrentUserDeps):
#     return user
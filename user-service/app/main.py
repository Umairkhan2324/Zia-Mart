from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
import time 
from app import settings
from app.db_engine import engine
from app.models.user_model import User,UserPublic,UserPublicWithRole,UserCreate,Token
from app.crud.user_crud import create_user,user_login,CurrentUser,get_all_users,update_user,get_user_by_id
from app.deps import get_session, GetProducer,DBSessionDep 
from app.crud.admin_user import create_admin_user

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)




# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating table....")
    create_db_and_tables()
    await create_admin_user()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="User Service Management",
    version="0.0.1",
    root_path="/user-service"
    
)



@app.get("/")
def read_root():
    return {"Hello": "user Service"}


@app.post("/register-user/", response_model=UserPublic)
async def user_registration(user: UserCreate, session: DBSessionDep,producer:GetProducer):
    """ Create a new user """
    try:
        new_user_registered = create_user(user_data=user,session=session)
        if new_user_registered:
            user_dict = {"username":new_user_registered.user_name,"email":new_user_registered.email,"phone":new_user_registered.phone,"full_name":new_user_registered.full_name}
            user_json = json.dumps(user_dict).encode("utf-8")
            print("User Json: ",user_json)
            await producer.send_and_wait("user_registrations",user_json)
        return new_user_registered
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    
    

@app.post("/user-login", response_model=Token)
def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends(OAuth2PasswordRequestForm)],session: Annotated[Session, Depends(get_session)]):
    """ Get all products from the database"""
    try:
        access_token = user_login(form_data=form_data,session=session)
        return access_token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# @app.post("/role-assign/", response_model=UserPublic)
# def get_single_product(user_data:UserCreate,session:DBSessionDep):
#     """ Get a single product by ID"""
#     try:
#         return role_assign_by_admin(user_data=user_data,session=session)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.get('/user/me',response_model=UserPublic)
async def get_user_me(user:CurrentUser):
    try:
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get('/token-verify',response_model=UserPublicWithRole)
async def token_verify(user:CurrentUser):
    try:
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/get-all-user",response_model=list[UserPublic])
def all_user(users:Annotated[UserPublic,Depends(get_all_users)]):
    try:
        return users
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/user-update/",response_model=UserPublic)
def user_update(user: Annotated[UserPublic, Depends(update_user)]):
    """ Update a single user inforamtion like email etc."""
    try:
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-user-by-id",response_model=UserPublic)
def user_by_id(user_id:int,session:DBSessionDep):
    try:
        return get_user_by_id(id=user_id,session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


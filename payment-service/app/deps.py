from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from typing import Annotated,Any
import requests

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

from app.db_engine import engine
from app import settings

# Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


ProducerDep = Annotated[AIOKafkaProducer,Depends(get_kafka_producer)]


def get_session():
    with Session(engine) as session:
        yield session

DBSessionDep = Annotated[Session, Depends(get_session)]




def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]):
    # print(f"Token: {token}")

    if token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    url = f"{settings.AUTH_SERVER_URL}/token-verify"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    # print( "AUTHENTICATED_USER_DATA" ,response.json())

    if response.status_code == 200:
        user_data = response.json()
        return user_data
    
    raise HTTPException(status_code=response.status_code, detail=f"{response.text}")
    

GetCurrentUserDep = Annotated[ Any, Depends(get_current_user)]

def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    url = f"{settings.AUTH_SERVER_URL}/user-login"
    data = {
        "username":form_data.username,
        "password":form_data.password
    }
    response = requests.post(url,data=data)
    if response.status_code == 200:
        return response.json()
    
    raise HTTPException(status_code=response.status_code,detail=f"{response.text}")

LoginForAccessTokenDep = Annotated[dict, Depends(get_login_for_access_token)]
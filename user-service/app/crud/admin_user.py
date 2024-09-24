from fastapi import HTTPException
from app import settings 
from app.models.user_model import User,AdminCreate
import json
from sqlmodel import Session,select 
from aiokafka import AIOKafkaProducer 
from app.db_engine import engine
from app.utils.security import get_password_hash

async def create_admin_user():
    with Session(engine) as session:
        admin_user = session.exec(select(User).where(User.user_name == settings.USERNAME)).one_or_none()
        # print(admin_user)
        if admin_user is None:
            # producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
            # await producer.start()
            try:
                admin_user_data = AdminCreate(user_name=settings.USERNAME,full_name=settings.FULLNAME,email=settings.EMAIL,phone=settings.PHONE,password=settings.PASSWORD)
                hashed_password = get_password_hash(admin_user_data.password)
                admin_data = User.model_validate(admin_user_data,update={"password":hashed_password})
                session.add(admin_data)
                session.commit()
                session.refresh(admin_data)
            except Exception as e: 
                raise HTTPException(status_code=500, detail=f"Error creating admin user: {e}")
        
                
                
            #     user_dict = {"username":admin_data.user_name,"email":admin_data.email,"phone":admin_data.phone,"full_name":admin_data.full_name}
            #     user_json = json.dumps(user_dict).encode("utf-8")
            #     print("User Json: ",user_json)
            #     await producer.send_and_wait("user_registrations",user_json)
            
            # finally:
            #     await producer.stop()
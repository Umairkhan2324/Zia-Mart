from typing import Annotated
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlmodel import Session, select

from datetime import timedelta,datetime,timezone
from jose import jwt,JWTError

from app.models.user_model import User,UserCreate,UserUpdate,UserPublic,Role,Token
from app.utils.security import verify_password,get_password_hash,create_access_token,ALGORITHM
from app.deps import DBSessionDep
from app import settings




reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="user-login"
)

TokenDep = Annotated[str,Depends(reusable_oauth2)]



def get_current_user(session:DBSessionDep , token:TokenDep):
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get('sub')
    
    except JWTError:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
    user = session.exec(select(User).where(User.user_name == username)).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
   
    return user

CurrentUser = Annotated[User,Depends(get_current_user)]
# create new costomer user
def create_user(user_data: UserCreate, session: Session):
    # print("Adding user to Database")
    hashed_password = get_password_hash(user_data.password)
    user = User.model_validate(user_data,update={"password":hashed_password})
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# user login and accesstoken
def user_login(form_data:OAuth2PasswordRequestForm,session: Session):
    user_in_db = session.exec(select(User).where(User.user_name == form_data.username)).first()
    if not user_in_db:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    if not verify_password(form_data.password,user_in_db.password):
        raise HTTPException(status_code=401,detail="Invalid username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(subject=user_in_db.user_name,expires_delta=access_token_expires)

    token_data = Token(access_token=access_token,expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60)

    return token_data
    
    

# role assign 
# def role_assign_by_admin(user_data:UserCreate,session:Session):
#     user_in_db = session.exec(select(User).where(User.user_name == user_data.user_name).where(User.email==user_data.email)).one_or_none()
#     if not user_in_db:
#         raise HTTPException(status_code=404,detail="invalid credentials")
    
#     if not verify_password(user_data.password,user_in_db.password):
#         raise HTTPException(status_code=404,detail="invalid credientials")
    
#     admin_role = session.exec(select(User).where(User.role == Role.admin)).one_or_none()

#     if admin_role is None:

#         user_in_db.role = Role.admin
#         session.add(user_in_db)
#         session.commit()
#         session.refresh(user_in_db)
#         return user_in_db
    
#     raise HTTPException(status_code=400, detail="Role already assigned to another user")
    



# get all user 
def get_all_users(session:DBSessionDep,user:CurrentUser):
    if not user.role == 'admin':
        raise HTTPException(status_code=403,detail="The user doesn't have enough privileges")
    users = session.exec(select(User)).all()
    return users


def update_user(user:CurrentUser,user_data:UserUpdate,session:DBSessionDep):
    email_exists = session.exec(select(User).where(User.email == user_data.email)).one_or_none()
    if email_exists and email_exists.id != user.id:
        raise HTTPException(status_code=400, detail=f"Email {user_data.email} is already in use.")
    

    user_db = session.get(User,user.id)
    if not user_db:
        raise HTTPException(status_code=404,detail="User not found")
    
    data = user_data.model_dump(exclude_unset=True)   
    user_db.sqlmodel_update(data,update={"updated_at":datetime.now()})
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db



def get_user_by_id(id:int,session:Session):
    user = session.get(User,id)
    if user is None:
        raise HTTPException(status_code=404,detail="user not found")
    
    return user
    
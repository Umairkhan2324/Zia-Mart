from contextlib import asynccontextmanager
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator, List
from aiokafka import AIOKafkaProducer
import asyncio
import json
from uuid import UUID
from datetime import datetime

from app import settings
from app.db_engine import engine
from app.models.payment_model import (
    Payment, PaymentMethod, PaymentCreate, PaymentStatus, PaymentPublic
)
from app.crud.payment_crud import (
    create_order_payment, payment_success_and_fail, payment_create_COD,
    payment_status_update, get_all_payment_data, get_payment_data,
    get_payment_data_latest, delete_payment_data
)
from app.deps import (
    DBSessionDep, ProducerDep, LoginForAccessTokenDep, GetCurrentUserDep
)
from app.utils.encode_and_decode import CustomJSONEncoder
from app.consumer.payment_consumer import payment_consume_messages

# Database initialization
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# Application lifespan manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield

# FastAPI app instance
app = FastAPI(
    lifespan=lifespan,
    title="Payment Service Management",
    version="0.0.1",
    root_path="/payment-service"
)

# Root endpoint
@app.get("/")
def read_root():
    return {"Hello": "payment service"}

# Authentication endpoint
@app.post("/auth/login")
def login(token: LoginForAccessTokenDep):
    return token

# Order payment processing endpoint
@app.post("/create-checkout-session")
async def order_payment(
    payment: PaymentCreate,
    user: GetCurrentUserDep,
    producer: ProducerDep,
    session: DBSessionDep
):
    try:
        payment_data = {
            "order_id": payment.order_id,
            "amount": payment.amount,
            "user_id": user['id'],
            "email": user['email']
        }
        return create_order_payment(payment=payment_data, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stripe payment success callback
@app.get("/stripe-callback/payment-success/")
async def payment_success(session_id: str):
    try:
        payload = payment_success_and_fail(session_id=session_id, payment_status=PaymentStatus.COMPLETED)
        if payload:
            payment_json = json.dumps(payload, cls=CustomJSONEncoder).encode("utf-8")
            print("payment_JSON:", payment_json)

            producer = AIOKafkaProducer(bootstrap_servers="broker:19092")
            await producer.start()
            try:
                await producer.send_and_wait("payment-status-event", payment_json)
            finally:
                await producer.stop()

            return {"message": "Payment succeeded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stripe payment fail callback
@app.get("/stripe-callback/payment-fail/")
async def payment_fail(session_id: str):
    try:
        payload = payment_success_and_fail(session_id=session_id, payment_status=PaymentStatus.FAILED)
        if payload:
            payment_json = json.dumps(payload, cls=CustomJSONEncoder).encode("utf-8")
            print("payment_JSON:", payment_json)

            producer = AIOKafkaProducer(bootstrap_servers="broker:19092")
            await producer.start()
            try:
                await producer.send_and_wait("payment-status-event", payment_json)
            finally:
                await producer.stop()

        return {"message": "Payment failed", "order_id": payload.get("order_id")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Cash on delivery payment endpoint
@app.post("/payment-cash-on-delivery")
async def cod(
    payment_data: PaymentCreate,
    user: GetCurrentUserDep,
    session: DBSessionDep,
    producer: ProducerDep
):
    try:
        payment = {
            "order_id": payment_data.order_id,
            "amount": payment_data.amount,
            "user_id": user['id'],
            "email": user['email'],
            "payment_status": "PENDING",
            "payment_method": "COD"
        }
        payment_create_COD(payment_data=payment, session=session)
        payment_json = json.dumps(payment, cls=CustomJSONEncoder).encode("utf-8")
        print("payment_JSON:", payment_json)

        await producer.send_and_wait("payment-status-event", payment_json)
        return {"message": "Payment succeeded"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Payment status update endpoint
@app.patch("/payment-status", response_model=PaymentPublic)
async def payment_status(
    payment_id: UUID,
    payment_status: PaymentStatus,
    user: GetCurrentUserDep,
    session: DBSessionDep,
    producer: ProducerDep
):
    if user['role'] == 'admin':
        try:
            updated_payment_data = payment_status_update(
                payment_id=payment_id, payment_status=payment_status, session=session
            )
            if updated_payment_data.payment_status == PaymentStatus.COMPLETED:
                payment_dict = {
                    "order_id": updated_payment_data.order_id,
                    "payment_status": updated_payment_data.payment_status,
                    "user_id": updated_payment_data.customer_id,
                    "amount": updated_payment_data.amount,
                    "payment_method": "COD"
                }
                payment_json = json.dumps(payment_dict, cls=CustomJSONEncoder).encode("utf-8")
                await producer.send_and_wait("payment-status-event", payment_json)

            return updated_payment_data
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")

# Get all payments data for admin
@app.get("/get-all-payments-data", response_model=List[PaymentPublic])
async def get_payments(user: GetCurrentUserDep, session: DBSessionDep):
    try:
        if user['role'] == 'admin':
            payments_data = get_all_payment_data(session=session)
            return payments_data
        else:
            raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get user's own payment data
@app.get("/get-payments-data/me", response_model=List[PaymentPublic])
async def get_payment(user: GetCurrentUserDep, session: DBSessionDep):
    try:
        payments_data = get_payment_data(customer_id=user['id'], session=session)
        return payments_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get specific payment data by payment ID for the current user
@app.get("/get-payment-data/me", response_model=PaymentPublic)
async def get_current_payment(payment_id: UUID, user: GetCurrentUserDep, session: DBSessionDep):
    try:
        payments_data = get_payment_data_latest(payment_id=payment_id, customer_id=user['id'], session=session)
        return payments_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete payment data for admin
@app.delete("/delete-payment-data")
async def delete_payment(payment_id: UUID, user: GetCurrentUserDep, session: DBSessionDep, producer: ProducerDep):
    if user['role'] == 'admin':
        try:
            response = delete_payment_data(payment_id=payment_id, session=session)
            return response
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")

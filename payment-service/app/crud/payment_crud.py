from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import datetime
from uuid import UUID

from app.models.payment_model import Payment, PaymentStatus, PaymentMethod
from app.utils.stripe_utils import create_stripe_session, stripe_session_retrieve
from app.db_engine import engine

# Create a new order payment and initiate Stripe checkout session
def create_order_payment(payment: dict, session: Session):
    try:
        # Create Stripe checkout session
        url = create_stripe_session(
            order_id=payment['order_id'],
            user_id=payment['user_id'],
            amount=int(payment['amount']),
            email=payment['email']
        )

        # Create and persist payment with Stripe as the payment method
        payment_method = PaymentMethod(payment_method='stripe')
        new_payment = Payment(
            order_id=payment['order_id'],
            amount=payment['amount'],
            customer_id=payment['user_id'],
            payment_method=payment_method
        )
        session.add(new_payment)
        session.commit()
        session.refresh(new_payment)

        return {"checkout_url": url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order payment: {e}")

# Handle payment success or failure
def payment_success_and_fail(session_id: str, payment_status: PaymentStatus):
    try:
        # Retrieve Stripe session details
        stripe_session = stripe_session_retrieve(session_id=session_id)

        with Session(engine) as db_session:
            payment = db_session.exec(
                select(Payment).where(Payment.order_id == UUID(stripe_session.metadata.order_id))
            ).first()

            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")

            # Update payment status and timestamp
            payment.payment_status = payment_status
            payment.updated_at = datetime.utcnow()

            db_session.add(payment)
            db_session.commit()
            db_session.refresh(payment)

            return {
                "order_id": payment.order_id,
                "payment_status": payment.payment_status,
                "user_id": payment.customer_id,
                "amount": payment.amount,
                "payment_method": "Stripe"
            }
    
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Error processing payment: {e}")

# Create a Cash On Delivery (COD) payment
def payment_create_COD(payment_data: dict, session: Session):
    payment_method = PaymentMethod(payment_method='COD')
    new_payment = Payment(
        order_id=payment_data['order_id'],
        amount=payment_data['amount'],
        customer_id=payment_data['user_id'],
        payment_method=payment_method
    )
    
    session.add(new_payment)
    session.commit()
    session.refresh(new_payment)
    
    return new_payment

# Update payment status by payment ID
def payment_status_update(payment_id: UUID, payment_status: PaymentStatus, session: Session):
    user_payment = session.get(Payment, payment_id)
    
    if not user_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Update status and timestamp
    user_payment.payment_status = payment_status
    user_payment.updated_at = datetime.utcnow()

    session.add(user_payment)
    session.commit()
    session.refresh(user_payment)

    return user_payment

# Retrieve all payment data
def get_all_payment_data(session: Session):
    return session.exec(select(Payment)).all()

# Retrieve payment data for a specific customer
def get_payment_data(customer_id: int, session: Session):
    return session.exec(select(Payment).where(Payment.customer_id == customer_id)).all()

# Retrieve the latest payment data for a customer by payment ID
def get_payment_data_latest(payment_id: UUID, customer_id: int, session: Session):
    return session.exec(
        select(Payment).where(Payment.customer_id == customer_id).where(Payment.id == payment_id)
    ).one_or_none()

# Delete payment data by payment ID
def delete_payment_data(payment_id: UUID, session: Session):
    customer_payment = session.get(Payment, payment_id)
    
    if not customer_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Retrieve the associated payment method for deletion
    payment_method = session.get(PaymentMethod, customer_payment.payment_method_id)

    # Delete payment and payment method
    session.delete(customer_payment)
    session.delete(payment_method)
    session.commit()

    return {"message": "Payment data deleted successfully"}

import stripe
from uuid import UUID
from fastapi import HTTPException
from app.settings import STRIPE_API_KEY

# Set Stripe API key
stripe.api_key = STRIPE_API_KEY

def create_stripe_session(order_id: UUID, user_id: int, amount: int, email: str) -> str:
    """Create a Stripe checkout session for payment."""
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": str(order_id),
                    },
                    "unit_amount": amount * 100,  # Amount in cents
                },
                "quantity": 1,
            }],
            allow_promotion_codes=True,
            invoice_creation=stripe.checkout.Session.CreateParamsInvoiceCreation(
                enabled=True
            ),
            metadata={
                "user_id": str(user_id),
                "email": email,
                "order_id": str(order_id),
            },
            mode="payment",
            success_url="http://localhost:9004/stripe-callback/payment-success/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:9004/stripe-callback/payment-fail/?session_id={CHECKOUT_SESSION_ID}",
            customer_email=email
        )
        return checkout_session.url

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create Stripe session: {e}")
def stripe_session_retrieve(session_id: str):
    """Retrieve an existing Stripe checkout session by session ID."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Stripe session: {e}")

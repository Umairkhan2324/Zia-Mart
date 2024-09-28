from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.order_model import Address, UpdateAddress, Order, OrderStatus, PaymentStatus, OrderItems
from uuid import UUID

# Add a new order to the database
def create_order(order_data: dict, session: Session):
    print("Adding order to Database")

    new_order = Order(
        total_price=0,
        address_id=order_data['address_id'],
        customer_id=order_data['customer_id']
    )

    # Add order items and calculate the total price
    for item in order_data['order_items']:
        price = item['price'] * item['quantity']
        order_item = OrderItems(
            product_id=item['product_id'],
            price=price,
            quantity=item['quantity']
        )
        new_order.order_items.append(order_item)

    new_order.total_price = sum(item.price for item in new_order.order_items)

    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    
    return new_order

# Add a new address to the database
def create_address(address_data: Address, session: Session):
    print("Adding address to Database")
    
    session.add(address_data)
    session.commit()
    session.refresh(address_data)
    
    return address_data

# Get addresses for a specific user by ID
def get_address(user_id: int, session: Session):
    return session.exec(select(Address).where(Address.user_id == user_id)).all()

# Update an existing address
def update_address(address_id: int, user_id: int, address: UpdateAddress, session: Session):
    user_address = session.exec(
        select(Address)
        .where(Address.id == address_id)
        .where(Address.user_id == user_id)
    ).one_or_none()

    if not user_address:
        raise HTTPException(status_code=404, detail="Address not found")

    address_data = address.model_dump(exclude_unset=True)
    user_address.sqlmodel_update(address_data)

    session.add(user_address)
    session.commit()
    session.refresh(user_address)
    
    return user_address

# Delete an address
def delete_address(address_id: int, user_id: int, session: Session):
    user_address = session.exec(
        select(Address)
        .where(Address.user_id == user_id)
        .where(Address.id == address_id)
    ).one_or_none()

    if not user_address:
        raise HTTPException(status_code=404, detail="Address not found")

    session.delete(user_address)
    session.commit()
    
    return {"message": "Address successfully removed"}

# Get orders for a specific customer
def get_customer_orders(customer_id: int, session: Session):
    return session.exec(select(Order).where(Order.customer_id == customer_id)).all()

# Update the status of an order
def order_status_update(order_id: UUID, order_status: OrderStatus, user_id: int, session: Session):
    order = session.exec(
        select(Order)
        .where(Order.id == order_id)
        .where(Order.customer_id == user_id)
    ).one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = order_status

    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order

# Update the payment status of an order
def order_payment_update(order_id: UUID, order_payment_status: PaymentStatus, session: Session):
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.payment_status = order_payment_status

    session.add(order)
    session.commit()
    session.refresh(order)
    
    return {"order_items": order.order_items}

# Get a specific order by order ID
def get_order(order_id: UUID, session: Session):
    return session.get(Order, order_id)

# Get all orders
def all_orders(session: Session):
    return session.exec(select(Order)).all()

# Verify if an order exists
def verify_order(order_id: UUID, session: Session):
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

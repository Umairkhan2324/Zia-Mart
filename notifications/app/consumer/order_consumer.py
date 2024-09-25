from aiokafka import AIOKafkaConsumer
import json
from app.utils.utils import send_email, get_user_by_id, email_content

async def consume_order_messages(topic, bootstrap_servers, group_id):
    """Consume order messages from Kafka, process order data, and send email notifications."""
    
    # Create the Kafka consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
    )
    
    print(f"Consumer started for topic: {topic}")
    
    # Start the Kafka consumer.
    await consumer.start()
    
    try:
        async for message in consumer:
            print(f"Received message from topic {message.topic}")
            
            try:
                order_data = json.loads(message.value.decode())
                print(f"Decoded order data: {order_data}")
                
                user_data = get_user_by_id(order_data['customer_id'])
                
                email_to = user_data['email']
                content = email_content({
                    "full_name": user_data['full_name'],
                    "order_number": order_data['id'],
                    "total_amount": order_data['total_price'],
                    "payment_status": order_data["payment_status"],
                    "order_status": order_data['status']
                }, "order_places.html")
                
                email_subject = f"Order Confirmation: {order_data['id']}"
                send_email(email_to=email_to, subject=email_subject, email_content_for_send=content)
                print(f"Order confirmation email sent to {email_to} for order {order_data['id']}.")
                
            except Exception as processing_error:
                print(f"Error processing message: {processing_error}")
    
    except Exception as e:
        print(f"Consumer error: {e}")
    
    finally:
        await consumer.stop()
        print(f"Consumer for topic {topic} has been stopped.")
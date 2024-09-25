from aiokafka import AIOKafkaConsumer
import json
from app.utils.utils import send_email, get_user_by_id, email_content
from app.utils.encode_and_decode import custom_decoder

async def consume_payment_status_message(topic, bootstrap_servers, group_id):
    """Consume payment status messages from Kafka, process data, and send email notifications."""
    
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
                payment_data = json.loads(message.value.decode(), object_hook=custom_decoder)
                print(f"Decoded payment data: {payment_data}")
                
                user_data = get_user_by_id(customer_id=payment_data['user_id'])
                
                if user_data is not None:
                    email_to = user_data['email']
                    
                    content = email_content({
                        "full_name": user_data['full_name'],
                        "order_number": payment_data['order_id'],
                        "payment_status": payment_data['payment_status'],
                        "payment_method": payment_data['payment_method'],
                        "app_name": "Zia Mart"
                    }, "payment_status.html")
                    
                    email_subject = f"Payment Confirmation: {payment_data['order_id']}"
                    send_email(email_to=email_to, subject=email_subject, email_content_for_send=content)
                    print(f"Payment confirmation email sent to {email_to} for order {payment_data['order_id']}.")
                
            except Exception as processing_error:
                print(f"Error processing payment message: {processing_error}")
    
    except Exception as e:
        print(f"Consumer error: {e}")
    
    finally:
        await consumer.stop()
        print(f"Consumer for topic {topic} has been stopped.")

from aiokafka import AIOKafkaConsumer
import json
from app.utils.utils import send_email, get_user_by_id, email_content
from app.utils.encode_and_decode import custom_decoder

async def consume_add_inventory_messages(topic, bootstrap_servers, group_id):
    """Consume inventory messages from Kafka, process data, and send email notifications."""
    
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
                inventory_data = json.loads(message.value.decode(), object_hook=custom_decoder)
                print(f"Decoded inventory data: {inventory_data}")
                
                user_data = get_user_by_id(inventory_data['user_id'])
                email_to = user_data['email']
                
                content = email_content({
                    "full_name": user_data['full_name'],
                    "product_id": inventory_data['product_id'],
                    "quantity": inventory_data['quantity']
                }, "add_inventory.html")
                
                email_subject = "Inventory Update Confirmation"
                send_email(email_to=email_to, subject=email_subject, email_content_for_send=content)
                print(f"Email sent to {email_to} regarding inventory update.")
                
            except Exception as processing_error:
                print(f"Error processing message: {processing_error}")
    
    except Exception as e:
        print(f"Consumer error: {e}")
    
    finally:
        await consumer.stop()
        print(f"Consumer for topic {topic} has been stopped.")

from aiokafka import AIOKafkaConsumer
import json
from app.utils.utils import send_email, email_content

async def consume_new_registed_user_messages(topic, bootstrap_servers, group_id):
    """Consume new registered user messages from Kafka and send welcome email notifications."""
    
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
                new_user_data = json.loads(message.value.decode())
                print(f"Decoded new user data: {new_user_data}")
                
                email_to = new_user_data['email']
                content = email_content({
                    "username": new_user_data['username'],
                    "email": new_user_data['email'],
                    "app_name": "Zia Mart",
                    "full_name": new_user_data['full_name'],
                    "phone": new_user_data['phone']
                }, "new_user_registration.html")
                
                email_subject = "Account Confirmed - Start Exploring Now"
                send_email(email_to=email_to, subject=email_subject, email_content_for_send=content)
                print(f"Welcome email sent to {email_to} for user {new_user_data['username']}.")
                
            except Exception as processing_error:
                print(f"Error processing new user registration message: {processing_error}")
    
    except Exception as e:
        print(f"Consumer error: {e}")
    
    finally:
        await consumer.stop()
        print(f"Consumer for topic {topic} has been stopped.")

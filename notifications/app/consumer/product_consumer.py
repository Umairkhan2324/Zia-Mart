from aiokafka import AIOKafkaConsumer
import json

from app.utils.utils import send_email,email_content,get_user_by_id


async def consume_product_messages(topic, bootstrap_servers,group_id):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        # auto_offset_reset="earliest",
    )
    print(f"life span send topic:{topic}")
    # Start the consumer.
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")

            product_data = json.loads(message.value.decode())
            print(f"Data {product_data}")
            
            user_data = get_user_by_id(product_data["user_id"])
            
            email_to = user_data['email']
            content= email_content({"full_name":user_data['full_name'],"product_name":product_data['name'],"product_id":product_data['id']},"add_product.html")
            email_subject = f"New Product Added: {product_data['name']}"
            send_email(email_to=email_to,subject=email_subject,email_content_for_send=content)
            
            
            
    except Exception as e:
        print(e)
            
    finally:
        await consumer.stop()
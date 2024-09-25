from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.deps import get_session
from app.core.encode_and_decode import custom_decoder
from app.crud.product_crud import verify_products

async def consumer_order_messages(topic,bootstrap_servers,group_id):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id
    )

    await consumer.start()

    try:
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")
            order_data = json.loads(message.value.decode(),object_hook=custom_decoder)
            with next(get_session()) as session:
                print("Checking if the product service order items is valid or not product order consumer.")


                is_verified = verify_products(products_data=order_data['order_items'],session=session)

                if is_verified['result']:
                    
                    producer = AIOKafkaProducer(bootstrap_servers="broker:19092")
                    await producer.start()
                    try:
                        await producer.send_and_wait("product-order-event-verified-product",message.value)
                    finally:
                        await producer.stop()
                else:
                    print(f"Error: Product ID {is_verified['product_id']} is not valid due to incorrect product or price information.")


                



    

    except Exception as e:
        print(e)

    finally:
        await consumer.stop()
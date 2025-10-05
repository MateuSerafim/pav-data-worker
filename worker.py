import pika
import os
from dotenv import load_dotenv
import time

from workers import pav_images_worker

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

time.sleep(25)
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()

channel.queue_declare(queue="survey-images", durable=True)
channel.basic_consume(queue="survey-images", 
                      on_message_callback=pav_images_worker.callback)

channel.start_consuming()
from dotenv import load_dotenv

load_dotenv()

import aio_pika
import os
import asyncio
from workers import pav_images_worker

async def main():
    print("Worker: pav image process - iniciado!")
    connection = await aio_pika.connect_robust(os.getenv("RABBITMQ_URL"))
    channel = await connection.channel()
    queue = await channel.declare_queue("survey-images", durable=True)
    await queue.consume(pav_images_worker.callback)
    
    try:
        await asyncio.Future()
    finally:
        await connection.close()

asyncio.run(main())
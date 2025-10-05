from utils.dependences import GeneralService

def callback(ch, method, properties, body):
    file_register_id = body.decode()
    print(file_register_id)

    ch.basic_ack(delivery_tag=method.delivery_tag)
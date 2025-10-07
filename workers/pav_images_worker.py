from utils.dependences import GeneralService
from core.src.images_module.pav_reader import ImageReader
import uuid
import aio_pika

async def callback(message: aio_pika.IncomingMessage):
    async with message.process():
        file_register_id = message.body.decode()

    print(f"processando imagem: {file_register_id}!")
    general_service = await GeneralService.create()
    
    try:
        register_maybe = await general_service.visual_register_service\
                                .get_visual_register(uuid.UUID(file_register_id))
        if (register_maybe.is_failure()):
            raise Exception()
        url = register_maybe.value.image_url
        print(url)

        file = await general_service.azure_storage_service.get_file("images-survey", url)
        if (file.is_failure()):
            raise Exception()
        image_data = await file.value.readall()
        image = ImageReader.read_from_blob_data(image_data, file_register_id)
        if (image.is_failure()):
            raise Exception()

        objects_detecteds = general_service.prediction_pav_service.check_pav_defects(image.value)
        print("_________________________________________________\n\n")
        print(f"Quantidade de objetos encontrados: {len(objects_detecteds)}!")
        print("\n\n_________________________________________________")

        # preciso otimizar, criando um método add_many
        for o in objects_detecteds:
            await general_service.object_register_service.add(o)

        register_maybe.value.process_status = 1
        await general_service.visual_register_service.update_visual_register(register_maybe.value)
        
    except Exception as e:
        register_maybe.value.process_status = 2
        await general_service.visual_register_service.update_visual_register(register_maybe.value)

        await message.nack()
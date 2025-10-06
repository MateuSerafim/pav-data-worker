import cv2
import numpy as np
import uuid
from core.src.images_module.pav_reader import ImageReader
from core.src.pavements_module.data_mapping.object_register import ObjectRegisterMapping

# 0 - remendo
# 1 - buraco
# 2 - trinca_s
# 3 - placa_i
# 4 - placa_r
# 5 - placa_a
# 6 - trinca_j

class PavPredictorService():
    def __init__(self, weigths_path:str, conf_threshold: float = 0.3):
        self.model = cv2.dnn.readNetFromONNX(weigths_path)
        self.conf_theshold = conf_threshold
    
    def check_pav_defects(self, image: ImageReader):
        h, w = image.image_data.shape[:2]

        blob = cv2.dnn.blobFromImage(image.image_data, 1/255.0, (640, 640), 
                                     swapRB=True, crop=False)
        self.model.setInput(blob)

        predictions = self.model.forward()[0]

        objects_list = []
        for p in range(predictions.shape[1]):
            object_maybe = self.__convert_prediction__(predictions[:, p], w, h, image.image_id)
            if (object_maybe != None):
                objects_list.append(object_maybe)
        
        return objects_list

    def __convert_prediction__(self, prediction, w, h, image_id):
        scores = prediction[5:]
        class_id = np.argmax(scores)

        if (class_id not in [0, 1, 2, 6]):
            return None

        confidence = scores[class_id] * prediction[4]
        if confidence < self.conf_theshold:
            return None
        
        cx, cy, bw, bh = prediction[:4]
        x_1 = int((cx - bw/2) * w / 640)
        y_1 = int((cy - bh/2) * h / 640)
        x_2 = int((cx + bw/2) * w / 640)
        y_2 = int((cy + bh/2) * h / 640)

        match class_id:
            case 0:
                class_type = 2
            case 1:
                class_type = 1
            case 2:
                class_type = 3
            case _:
                class_type = 4

        return ObjectRegisterMapping.create(class_type, confidence, 
                                            [x_1, y_1, x_2, y_2], image_id)
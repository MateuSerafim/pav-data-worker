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
    def __init__(self, weigths_path:str, 
                 conf_threshold: float = 0.3, 
                 nms_threshold: float = 0.45):
        self.model = cv2.dnn.readNetFromONNX(weigths_path)
        self.conf_theshold = conf_threshold
        self.nms_threshold = nms_threshold

    def check_pav_defects(self, image: ImageReader):
        h, w = image.image_data.shape[:2]

        blob = cv2.dnn.blobFromImage(image.image_data, 1/255.0, (640, 640), 
                                     swapRB=True, crop=False)
        self.model.setInput(blob)

        predictions = self.model.forward()[0]

        classes, boxes, confidences = self.__convert_predictions__(predictions)
        
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 
                                score_threshold = self.conf_theshold, 
                                nms_threshold = self.nms_threshold)
        
        objects_list = []
        for detect_pos in range(len(classes)):
            if detect_pos not in idxs:
                continue
            x_1 = int((boxes[detect_pos][0] - boxes[detect_pos][2] / 2)*w/640)
            y_1 = int((boxes[detect_pos][1] - boxes[detect_pos][3] / 2)*h/640)
            x_2 = int((boxes[detect_pos][0] + boxes[detect_pos][2] / 2)*w/640)
            y_2 = int((boxes[detect_pos][1] + boxes[detect_pos][3] / 2)*h/640)

            objects_list.append(\
                ObjectRegisterMapping.create(classes[detect_pos], confidences[detect_pos], 
                                             [x_1, y_1, x_2, y_2], image.image_id))
        
        return objects_list

    def __convert_predictions__(self, predictions):
        classes = []
        boxes = []
        confidences = []
        for p in range(predictions.shape[1]):
            pred = predictions[:, p]
            
            class_scores = pred[4:]
            class_id = np.argmax(class_scores)
            if (class_id not in [0, 1, 2, 6]):
                continue
            
            if np.max(class_scores) < self.conf_theshold:
                continue
            
            confidences.append(np.max(class_scores))
            boxes.append([int(pred[0]), int(pred[1]), int(pred[2]), int(pred[3])])

            match class_id:
                case 0:
                    class_type = 2
                case 1:
                    class_type = 1
                case 2:
                    class_type = 3
                case _:
                    class_type = 4
            
            classes.append(class_type)
        return classes, boxes, confidences
from core.src.pavements_module.services.road_stretch import RoadStretchService
from core.src.pavements_module.services.visual_survey import VisualSurveyService
from core.src.pavements_module.services.visual_register import VisualRegisterService
from core.src.pavements_module.services.object_register import ObjectRegisterService

from core.src.files_module.image_storage_service import AzureStorageService

from pav_predict_module.pav_preditor import PavPredictorService

from core.src.database.db_context import get_session

import os

class GeneralService():
    def __init__(self, db_session):
        self.road_stretch_service = RoadStretchService(db_session)
        self.visual_survey_service = VisualSurveyService(db_session, self.road_stretch_service)
        self.visual_register_service = VisualRegisterService(db_session, self.visual_survey_service)
        self.object_register_service = ObjectRegisterService(db_session, self.visual_register_service)
        self.azure_storage_service = AzureStorageService(os.getenv("STORAGE_CONNECTION_STRING"))
        self.prediction_pav_service = PavPredictorService(os.getenv("CNN_WEIGHTS_PATH"), 
                                                          float(os.getenv("CNN_CONF_THRESHOLD", 0.3)),
                                                          float(os.getenv("CNN_CONF_NMS_THRESHOLD", 0.45)))
    
    @staticmethod
    async def create():
        async with get_session() as session:
            return GeneralService(session)
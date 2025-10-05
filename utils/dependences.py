from core.src.pavements_module.services.road_stretch import RoadStretchService
from core.src.pavements_module.services.visual_survey import VisualSurveyService
from core.src.pavements_module.services.visual_register import VisualRegisterService

from core.src.files_module.image_storage_service import AzureStorageService

from core.src.database.db_context import get_session

import os

class GeneralService():
    def __init__(self, db_session):
        self.road_stretch_service = RoadStretchService(db_session)
        self.visual_survey_service = VisualSurveyService(db_session, self.road_stretch_service)
        self.visual_register_service = VisualRegisterService(db_session, self.visual_survey_service)
        self.azure_storage_service = AzureStorageService(os.getenv("STORAGE_CONNECTION_STRING"))
    
    @staticmethod
    async def create():
        db_session = await get_session()

        return GeneralService(db_session)
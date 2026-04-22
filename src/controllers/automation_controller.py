# Gestiona desde la UI el inicio, seguimiento y cierre de la automatización.
import logging
from collections.abc import Callable

from src.models.excel_models import ExcelResult

from src.services.automation_services import AutomationService

logger = logging.getLogger(__name__)

class AutomationController:
    def __init__(self):
        self.automation_service = AutomationService()

    def start_process(self, excel_result: ExcelResult, emit: Callable[[object], None]) -> None:
        logger.info("Iniciando carga de ticket para archivo: %s", excel_result.excel_path)
        self.automation_service.start_process(excel_result=excel_result, emit=emit)
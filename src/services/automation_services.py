import logging
from collections.abc import Callable

from src.models.excel_models import ExcelResult
from src.models.process_event import (
    ProcessRowResult,
    ProcessStatusUpdate,
    ProcessCompleted,
    ProcessFailed,
)
from src.services.auth_service import AuthService
from src.services.ticket_service import TicketService
from src.utils.exceptions import AutomationError

from src.models.ticket_job import JobStatus

logger = logging.getLogger(__name__)

class AutomationService:
    def __init__(self):
        self.auth_service = AuthService()

    def start_process(self, excel_result: ExcelResult, emit: Callable[[object], None]) -> None:
        ticket_service = TicketService()
        browser_manager = None

        try:
            emit(ProcessStatusUpdate("Iniciando navegador..."))

            page, browser_manager = self.auth_service.start_authenticated_page()

            jobs = [job for job in excel_result.jobs if not job.is_finished()]
            total = len(jobs)
            processed = 0

            if total == 0:
                emit(ProcessStatusUpdate("No hay filas pendientes por procesar."))
                emit(ProcessCompleted("No había tickets pendientes.", 0, 0))
                return

            emit(ProcessStatusUpdate("Login detectado. Iniciando carga de tickets..."))

            for job in jobs:
                processed += 1
                emit(ProcessStatusUpdate(f"Procesando fila {job.row_id} ({processed}/{total})...", processed, total,))

                try:
                    result = ticket_service.process_job(page=page, job=job, excel_result=excel_result,)
                except Exception as e:
                    logger.exception("Error procesando fila %s", job.row_id)
                    job.error = str(e)

                    if job.status == JobStatus.CREATE_IN_PROGRESS:
                        job.status = JobStatus.FAILED_CREATE
                    elif job.status == JobStatus.CLOSE_IN_PROGRESS:
                        job.status = JobStatus.FAILED_CLOSE

                    result = ProcessRowResult(row_id=job.row_id, status=job.status.value, ticket_id=job.ticket_id, error=job.error,)

                    if self._is_fatal_excel_error(e):
                        emit(ProcessFailed("Error crítico en Excel", "Se detuvo el proceso porque el archivo Excel quedó inválido o no se pudo guardar.\n\n" f"Detalle: {str(e)}",))
                        return

                emit(result)

            emit(ProcessStatusUpdate("Proceso finalizado.", total, total))
            emit(ProcessCompleted("Tickets cargados con éxito.", total, total))

        except Exception as e:
            logger.exception("Error general en automatización")
            raise AutomationError(f"Error en automatización {str(e)}") from e

        finally:
            if browser_manager:
                browser_manager.close()

    def _is_fatal_excel_error(self, error: Exception) -> bool:
        text = str(error).lower()

        fatal_patterns = [
            "[content_types].xml",
            "i/o operation on closed file",
            "file is not a zip file",
            "permission denied",
            "permissionerror",
        ]

        return any(pattern in text for pattern in fatal_patterns)
import logging

from src.manager.settings_manager import SettingsManager
from src.automation.flows.create_ticket_flow import CreateTicketFlow
from src.automation.flows.close_ticket_flow import CloseTicketFlow

from src.models.process_event import ProcessRowResult
from src.models.ticket_job import JobStatus, TicketJob
from src.models.excel_models import ExcelResult

from src.excel.writer import ExcelWriter

from src.utils.exceptions import (
    JobValidationError,
    RetryableUIError,
    TicketProcessError,
    UncertainTicketCreationError,
    UncertainTicketCloseError,
)

logger = logging.getLogger(__name__)

class TicketService:
    def __init__(self):
        self.settings_manager = SettingsManager()

    def process_job(self, page, job: TicketJob, excel_result: ExcelResult) -> ProcessRowResult:
        logger.info("Procesando job fila %s con status=%s", job.row_id, job.status)

        if job.is_finished():
            return ProcessRowResult(
                row_id=job.row_id,
                status=JobStatus.CLOSED.value,
                ticket_id=job.ticket_id,
                error=None,
            )

        if job.needs_create():
            return self._process_main_flow(page=page, job=job, excel_result=excel_result)

        raise JobValidationError(
            f"La fila {job.row_id} no tiene un estado procesable: {job.status}"
        )

    def _process_main_flow(self, page, job: TicketJob, excel_result: ExcelResult) -> ProcessRowResult:
        settings = self.settings_manager.get_settings()
        report_user = settings["report_user"]
        job_group = settings["job_group"]

        writer = ExcelWriter(excel_result)
        current_stage = "create"

        try:
            job.status = JobStatus.CREATE_IN_PROGRESS
            job.error = None

            ticket_id = self._run_create_part(
                page=page,
                job=job,
                writer=writer,
                report_user=report_user,
                job_group=job_group,
            )

            job.status = JobStatus.CREATED
            job.ticket_id = ticket_id
            job.error = None

            current_stage = "close"
            job.status = JobStatus.CLOSE_IN_PROGRESS

            self._run_close_part(page=page, job=job)

            job.status = JobStatus.CLOSED
            job.error = None

            return ProcessRowResult(
                row_id=job.row_id,
                status=job.status.value,
                ticket_id=job.ticket_id,
                error=job.error,
            )

        except UncertainTicketCreationError as e:
            logger.warning("Creación incierta en fila %s: %s", job.row_id, e)
            job.status = JobStatus.CREATE_UNCERTAIN
            job.error = str(e)

            return ProcessRowResult(
                row_id=job.row_id,
                status=job.status.value,
                ticket_id=job.ticket_id,
                error=job.error,
            )

        except UncertainTicketCloseError as e:
            logger.warning("Cierre incierto en fila %s: %s", job.row_id, e)
            job.status = JobStatus.CLOSE_UNCERTAIN
            job.error = str(e)

            return ProcessRowResult(
                row_id=job.row_id,
                status=job.status.value,
                ticket_id=job.ticket_id,
                error=job.error,
            )

        except TicketProcessError as e:
            logger.warning("Error controlado en flujo principal. fila=%s stage=%s error=%s", job.row_id, current_stage, e,)

            job.error = str(e)

            if current_stage == "create":
                job.status = JobStatus.FAILED_CREATE
            else:
                job.status = JobStatus.FAILED_CLOSE

            return ProcessRowResult(
                row_id=job.row_id,
                status=job.status.value,
                ticket_id=job.ticket_id,
                error=job.error,
            )

        finally:
            writer.close()

    def _run_create_part(self, page, job: TicketJob, writer: ExcelWriter, report_user: str, job_group: str) -> str:
        max_attempts = 3
        last_err = None

        for attempt in range(1, max_attempts + 1):
            flow = CreateTicketFlow(page)

            try:
                logger.info("Fila %s - create attempt %s/%s", job.row_id, attempt, max_attempts)

                flow.open_new_incident()

                creation_dt_text = flow.ensure_creation_datetime(job)
                job.creation_dt_text = creation_dt_text

                writer.add_datetime(job)
                writer.add_time(job)

                flow.select_notificado_por(report_user)
                flow.input_titulo_descripcion(job)
                flow.select_tipo_solicitud_servicio()
                flow.select_categoria()
                flow.select_servicio()
                flow.select_2da_linea()
                flow.select_grupo_responsable(job_group)
                flow.select_tecnico_encargado()

                ticket_id = flow.crear_ticket()
                job.ticket_id = ticket_id
                writer.add_ticket(job)
                writer.save()

                logger.info("Fila %s creada correctamente. ticket_id=%s", job.row_id, job.ticket_id)
                return ticket_id

            except RetryableUIError as e:
                last_err = e
                logger.warning(
                    "Error UI reintentable creando fila %s. Reintento %s/%s. Error: %s",
                    job.row_id, attempt, max_attempts, e
                )
                flow.go_home()

                if attempt >= max_attempts:
                    raise TicketProcessError(
                        f"No se pudo crear la fila {job.row_id} tras {max_attempts} reintentos. Último error: {e}"
                    ) from e

                continue

            except UncertainTicketCreationError:
                flow.go_home()
                raise

            except Exception as e:
                logger.exception("Error no controlado creando fila %s", job.row_id)
                flow.go_home()
                raise TicketProcessError(str(e)) from e

        raise TicketProcessError(
            f"No se pudo crear la fila {job.row_id}. Último error: {last_err}"
        ) from last_err

    def _run_close_part(self, page, job: TicketJob) -> None:
        if not job.ticket_id:
            raise JobValidationError(f"La fila {job.row_id} no tiene ticket_id para cerrar.")

        flow = CloseTicketFlow(page)

        try:
            logger.info("Fila %s - close ticket_id=%s", job.row_id, job.ticket_id)

            flow.select_editar_tkt()
            flow.select_investigacion()
            flow.select_investigacion_resolucion()
            flow.input_solucion_tkt(job)
            flow.close_ticket()
            flow.go_home()

            logger.info("Fila %s cerrada correctamente. ticket_id=%s", job.row_id, job.ticket_id)

        except JobValidationError:
            raise

        except UncertainTicketCloseError:
            flow.go_home()
            raise

        except RetryableUIError as e:
            flow.go_home()
            raise UncertainTicketCloseError(
                f"No se pudo completar el cierre y se perdió el contexto del ticket: {e}"
            ) from e

        except Exception as e:
            logger.exception("Error no controlado cerrando fila %s", job.row_id)
            flow.go_home()
            raise UncertainTicketCloseError(
                f"No se pudo confirmar el cierre del ticket: {e}"
            ) from e
import logging
from queue import Queue, Empty
from threading import Thread
from collections.abc import Callable

from src.controllers.app_controller import AppController
from src.controllers.automation_controller import AutomationController

from src.models.process_event import (
    ProcessRowResult,
    ProcessStatusUpdate,
    ProcessCompleted,
    ProcessFailed,
)

from src.utils.exceptions import ExcelResultEmpty, ProcessRuninngError

from src.ui.views.process_view import ProcessView

logger = logging.getLogger(__name__)

class ProcessController:
    def __init__(self, app_controller: AppController, automation_controller: AutomationController):
        self.app_controller = app_controller
        self.automation_controller = automation_controller
        self.view: ProcessView | None = None

        self._queue = Queue()
        self._worker: Thread | None = None
        self._is_running = False

    def start(self, view: ProcessView,):
        if self._is_running:
            raise ProcessRuninngError("Ya existe un proceso en curso")

        self.view = view
        excel_path, excel_result = self.app_controller.get_excel_context()
        
        if not excel_result or not excel_path:
            raise ExcelResultEmpty("No se ha cargado ningun archivo excel")

        self._queue = Queue()
        
        view.reset_view()
        view.set_status("Iniciando proceso...")
        view.load_jobs(excel_result.jobs)

        task = lambda: self.automation_controller.start_process(excel_result=excel_result, emit=self._queue.put)
               
        self._start_worker(task)
        self._poll_queue()

    def _start_worker(self, task: Callable[[], None]) -> None:
        self._is_running = True
        self._worker = Thread(target=self._run_worker, args=(task,), daemon=True)
        self._worker.start()

    def _run_worker(self, task: Callable[[], None]) -> None:
        try:
            task()
        except Exception as e:
            logger.exception("Error no controlado en worker del proceso")
            self._queue.put(ProcessFailed("Error en automatización", str(e)))
        finally:
            self._is_running = False

    def _poll_queue(self) -> None:
        if self.view is None:
            return

        while True:
            try:
                event = self._queue.get_nowait()
            except Empty:
                break

            self._handle_event(event)

        if self._is_running or not self._queue.empty():
            self.app_controller.window.after(100, self._poll_queue)
        else:
            self._worker = None

    def _handle_event(self, event: object) -> None:
        if self.view is None:
            return

        if isinstance(event, ProcessStatusUpdate):
            self.view.set_status(event.message)
            return

        if isinstance(event, ProcessRowResult):
            self.view.update_job_status(
                event.row_id,
                event.status,
                event.ticket_id,
                event.error,
            )
            return

        if isinstance(event, ProcessCompleted):
            self.view.set_status(event.message)
            self.view.show_completed(event.message)
            return

        if isinstance(event, ProcessFailed):
            self.view.show_error_message(event.title, event.message)
            return

        logger.warning("Evento de proceso no reconocido: %r", event)

    # Detener todo antes y volver
    def on_back(self):
        if self._is_running and self.view is not None:
            raise ProcessRuninngError("No puedes volver mientras la automatización está en curso.",)
        self.app_controller.go_to("upload")
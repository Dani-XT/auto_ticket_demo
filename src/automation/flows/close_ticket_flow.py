import logging

from src.automation import selectors as s
from src.automation.flows.base_flow import BaseFlow

from src.models.ticket_job import TicketJob

from src.utils.exceptions import TicketProcessError, UncertainTicketCloseError

logger = logging.getLogger(__name__)


class CloseTicketFlow(BaseFlow):
    def select_editar_tkt(self):
        def action():
            logger.info("Editando Ticket")
            self._safe_click(s.EDIT_TICKET_BUTTON)

        return self._run_step(action, "No se pudo editar Ticket creado.")

    def select_investigacion(self):
        def action():
            locator, _ = self._find_visible(s.SAVE_CHANGES_BUTTON)

            if locator.is_visible():
                logger.info("Abriendo pestaña Investigacion")
                self._safe_click(s.INVESTIGATION_TAB_BUTTON)
            


        return self._run_step(action, "No se pudo seleccionar el boton de INVESTIGACION.")

    def select_investigacion_resolucion(self):
        def action():
            logger.info("Abriendo subpestaña de Resolucion")
            self._safe_click(s.RESOLUTION_TAB_BUTTON)

        return self._run_step(action, "No se pudo seleccionar el boton de RESOLUCION.")

    def input_solucion_tkt(self, job: TicketJob):
        def action():
            logger.info("Ingresando Solucion del Ticket")

            solucion = job.data["SOLUCION"].strip()
            if not solucion:
                raise TicketProcessError("La columna SOLUCION está vacía.")

            locator, _ = self._find_visible(s.INPUT_SOLUTION)
            locator.click(timeout=5_000)
            locator.fill("")
            locator.type(solucion, delay=0)

        return self._run_step(action, "No se pudo agregar solución.")

    def close_ticket(self):
        
        try:
            logger.info("Cerrando Ticket")
            self._safe_click(s.CLOSE_TICKET)

            locator, _ = self._find_visible(s.EDIT_TICKET_BUTTON)
            if not locator.is_visible():
                raise UncertainTicketCloseError("Se presionó el botón de firma, pero no se pudo confirmar que la solución quedara firmada por el técnico actual.")

        except UncertainTicketCloseError:
            raise
        except Exception as e:
            raise UncertainTicketCloseError(
                "Se presionó el botón de cerrar, pero no se pudo confirmar que el ticket fue cerrado."
            ) from e
        
        

    
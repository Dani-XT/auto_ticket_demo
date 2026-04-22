import logging
from datetime import date

from src.automation.flows.base_flow import BaseFlow
from src.automation import selectors as s
from src.automation.waits import (
    get_label_popup_txt,
    select_popup_option_by_text,
    parse_month_year_es,
    select_popup_option_by_attr_contains,
    get_tree_popup,
    tree_wait_label_visible,
    tree_expand,
    tree_click_leaf,
    click_radio_btn,
)
from src.utils.datetime_utils import parse_excel_date_text, parse_excel_time_text, parse_text_datetime
from src.utils.exceptions import TicketProcessError, UncertainTicketCreationError



logger = logging.getLogger(__name__)


class CreateTicketFlow(BaseFlow):

    def open_new_incident(self):
        logger.info("Abriendo nueva incidencia")
        self._safe_click(s.NEW_INCIDENT, timeout_ms=60_000, expect_nav=True,)

    def ensure_creation_datetime(self, job):
        excel_date = job.data.get("FECHA")
        excel_time = job.data.get("HORA")

        

        current_web_txt = self._get_label(s.CREATION_LABEL)
        current_web_dt = parse_text_datetime(current_web_txt)

        if not excel_date and not excel_time:
            logger.warning("Sin fecha en Excel, se usará fecha actual web: %s", current_web_txt)
            return current_web_txt

        if not excel_date:
            logger.warning(
                "Sin fecha en Excel, se usará la hora actual web para la fecha indicada: %s",
                current_web_dt.date(),
            )
            excel_date = current_web_dt.date()

        if not excel_time:
            logger.warning(
                "Sin hora en Excel, se usará la hora actual web para la fecha indicada: %s",
                current_web_dt.time(),
            )
            excel_time = current_web_dt.time()

        # CAMBIA INSTANCIA
        if isinstance(excel_date, str):
            excel_date = parse_excel_date_text(excel_date)

        if isinstance(excel_time, str):
            excel_time = parse_excel_time_text(excel_time)

        self._calendar_date(excel_date)
        self._calendar_hours(excel_time.hour)
        self._calendar_minute(excel_time.minute)

        return self._get_label(s.CREATION_LABEL)

    def _calendar_date(self, excel_date: date):
        def action():
            self._safe_click(s.CREATION_DATE_BUTTON)
            popup = self._wait_popup("span.pawCalPopup", must_contain_selector="td#pawTheLabelTgt")
            self._calendar_year_month(popup, excel_date.year, excel_date.month)
            self._calendar_day(popup, excel_date)

        return self._run_step(action, "No se pudo abrir o completar la selección de la fecha.",)

    def _calendar_year_month(self, popup, target_year: int, target_month: int):
        logger.info("Seleccionando Año y Mes")

        prev_btn = popup.locator("td[paw\\:cmd='prm']")
        next_btn = popup.locator("td[paw\\:cmd='nxm']")

        prev_btn.wait_for(state="visible", timeout=10_000)
        next_btn.wait_for(state="visible", timeout=10_000)

        target = (target_year, target_month)

        for _ in range(24):
            fecha_txt = get_label_popup_txt(
                self.page,
                popup_selector="span.pawCalPopup",
                label_selector="td#pawTheLabelTgt",
            )
            cy, cm = parse_month_year_es(fecha_txt)
            current = (cy, cm)

            if current == target:
                return

            if current < target:
                next_btn.click()
            else:
                prev_btn.click()

            self.page.wait_for_timeout(150)

        raise TicketProcessError(f"No pude llegar al mes objetivo {target_month}/{target_year}")

    def _calendar_day(self, popup, d: date):
        def action():
            logger.info("Seleccionando Día")
            day_id = f"pawDay_{d.year:04d}{d.month:02d}{d.day:02d}"
            day = popup.locator(f"td#{day_id}")

            if day.count() == 0:
                raise TicketProcessError(f"No se encontró el día en el popup: {day_id}")

            day.wait_for(state="visible", timeout=10_000)
            day.click()

        return self._run_step(action, "No se pudo seleccionar el día en el calendario.")

    def _calendar_hours(self, hour: int):
        def action():
            logger.info("Seleccionando Hora")
            self._safe_click(s.CREATION_HOURS_BUTTON)
            popup = self._wait_popup("span.pawDFSelPopup", must_contain_selector="td.pawOptTdr")
            select_popup_option_by_text(page=self.page, popup=popup, option_selector="td.pawOptTdr", target_text=str(hour))

        return self._run_step(action, f"No se pudo seleccionar la hora '{hour}'.",)

    def _calendar_minute(self, minute: int):
        def action():
            logger.info("Seleccionando Minutos")
            self._safe_click(s.CREATION_MINUTES_BUTTON)
            popup = self._wait_popup("span.pawDFSelPopup", must_contain_selector="td.pawOptTdr")

            try:
                select_popup_option_by_text(page=self.page, popup=popup, option_selector="td.pawOptTdr", target_text=str(minute))
            except Exception:
                select_popup_option_by_text(page=self.page, popup=popup, option_selector="td.pawOptTdr", target_text=f"{minute:02d}")

        return self._run_step(action, f"No se pudo seleccionar el minuto '{minute}'.")

    def select_notificado_por(self, report_user: str):
        def action():
            logger.info("Seleccionando Notificado Por")

            self._safe_click(s.NOTIFICADO_POR_FIELD, require_enabled=False)
            popup = self._wait_popup(s.NOTIFICADO_POR_POPUP, must_contain_selector="input.pawDFSelFilterTableInp")

            inp = popup.locator("input.pawDFSelFilterTableInp")
            inp.wait_for(state="visible", timeout=10_000)
            inp.fill("")
            inp.type(report_user, delay=0)

            try:
                inp.press("Enter")
            except Exception:
                pass

            needle = f"\\{report_user}"
            select_popup_option_by_attr_contains(page=self.page, popup=popup, attr="completeview", needle=needle)

        return self._run_step(action, f"No se pudo seleccionar el usuario reportante '{report_user}'.")

    def input_titulo_descripcion(self, job):
        def action():
            logger.info("Ingresando Problema y Descripción")

            problema = job.data["PROBLEMA"].strip()
            titulo = problema[:256]

            if not problema:
                raise TicketProcessError("La columna PROBLEMA está vacía.")

            locator, _ = self._find_visible(s.INCIDENT_TITLE)
            locator.fill("")
            locator.type(titulo, delay=0)

            locator, _ = self._find_visible(s.DESCRIPTION)
            locator.click(timeout=5_000)
            locator.fill("")
            locator.fill(problema)

        return self._run_step(action, "No se pudo ingresar el título y la descripción del ticket.")

    def select_tipo_solicitud_servicio(self):
        def action():
            logger.info("Seleccionando Solicitud de Servicio")

            self._safe_click(s.TIPO_SOLICITUD_BUTTON)
            popup = self._wait_popup(s.TIPO_SOLICITUD_POPUP, must_contain_selector="div.pawOpt")
            select_popup_option_by_text(page=self.page, popup=popup, option_selector="div.pawOpt", target_text="Solicitud de Servicio")

        return self._run_step(action, "No se pudo seleccionar 'Solicitud de Servicio'.")

    def select_categoria(self):
        def action():
            logger.info("Seleccionando Servicio")

            _, btn_frame = self._safe_click(s.CATEGORIA_BUTTON)

            popup = get_tree_popup(btn_frame, root_label="Servicio")

            tree_expand(self.page, popup, "Servicios TI")
            tree_wait_label_visible(popup, "Computadores e Impresoras")
            tree_expand(self.page, popup, "Computadores e Impresoras")
            tree_wait_label_visible(popup, "Computadores")
            tree_click_leaf(self.page, popup, "Computadores")

        return self._run_step(action, "No se pudo seleccionar la categoría 'Computadores'.")

    def select_servicio(self):
        def action():
            logger.info("Seleccionando Categoría")

            _, btn_frame = self._safe_click(s.SERVICIO_BUTTON)

            popup = get_tree_popup(btn_frame, root_label="Categorías", timeout=20_000)
            tree_click_leaf(self.page, popup, "Mantención de Equipos")

        return self._run_step(action, "No se pudo seleccionar el servicio 'Mantención de Equipos'.")

    def select_2da_linea(self):
        def action():
            logger.info("Seleccionando Escalar a 2da Línea")
            click_radio_btn(self.page, s.FIRST_LINE_RADIO_ROW)
            self.page.wait_for_timeout(400)

        return self._run_step(action, "No se pudo seleccionar 'Escalar a 2da Línea'.")

    def select_grupo_responsable(self, job_group: str):
        def action():
            logger.info("Seleccionando Grupo Responsable")

            self._safe_click(s.GRUPO_RESPONSABLE_BUTTON)

            popup = self._wait_popup(s.GRUPO_RESPONSABLE_POPUP, must_contain_selector="input.pawDFSelFilterTableInp")

            inp = popup.locator("input.pawDFSelFilterTableInp")
            inp.wait_for(state="visible", timeout=10_000)
            inp.fill("")
            inp.type(job_group, delay=0)

            try:
                inp.press("Enter")
            except Exception:
                pass

            select_popup_option_by_attr_contains(page=self.page, popup=popup, attr="paw:label", needle=job_group, timeout_ms=20_000, case_insensitive=True)

        return self._run_step(action, f"No se pudo seleccionar el grupo responsable '{job_group}'.")

    def select_tecnico_encargado(self):
        def action():
            logger.info("Seleccionando Técnico Asignado")

            tecnico = self._get_label(s.USER_INFO_LABEL)

            self._safe_click(s.TECNICO_ENCARGADO_BUTTON)
            popup = self._wait_popup(s.TECNICO_ENCARGADO_POPUP, must_contain_selector="input.pawDFSelFilterTableInp")

            inp = popup.locator("input.pawDFSelFilterTableInp")
            inp.wait_for(state="visible", timeout=10_000)
            inp.fill("")
            inp.type(tecnico, delay=0)

            try:
                inp.press("Enter")
            except Exception:
                pass

            select_popup_option_by_attr_contains(page=self.page, popup=popup, attr="paw:label", needle=tecnico, timeout_ms=20_000)

        return self._run_step(action, "No se pudo seleccionar el técnico encargado.",)

    def crear_ticket(self) -> str:
        logger.info("Creando ticket")
        self._safe_click(s.CREATE_TICKET_BUTTON)

        try:
            self._find_visible(s.EDIT_TICKET_BUTTON, timeout_ms=30_000)
        except Exception as e:
            raise UncertainTicketCreationError("Se presionó el botón de crear, pero no se pudo confirmar si el ticket fue creado.") from e
        
        ticket_text = self._get_label(s.CREATED_TICKET_LABEL, timeout_ms=15_000)

        if not ticket_text:
            raise UncertainTicketCreationError(f"No se pudo confirmar el ticket creado. Texto recibido: {ticket_text}")
        
        return ticket_text
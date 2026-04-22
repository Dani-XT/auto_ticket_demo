import logging

from src.automation.flows.base_flow import BaseFlow

from src.app.config import URL_PROACTIVA
from src.automation.waits import find_in_all_frames

logger = logging.getLogger(__name__)


class LoginFlow(BaseFlow):
    def __init__(self, page, browser_manager, auth_repository):
        super().__init__(page)
        self.browser_manager = browser_manager
        self.auth_repository = auth_repository

    def open_home(self):
        logger.info("Abriendo Proactiva")
        self.page.goto(URL_PROACTIVA, wait_until="domcontentloaded", timeout=60_000)

    def wait_for_login(self, timeout_ms: int = 180_000):
        logger.info("Esperando autenticación del usuario")

        try:
            locator, _ = self._find_visible("#newIncident", timeout_ms=timeout_ms)
        except Exception as e:
            raise RuntimeError(
                "No se detectó autenticación en ProactivaNet. "
                "Inicia sesión manualmente y asegúrate de llegar a la pantalla principal."
            ) from e

        logger.info("Login detectado, guardando sesión")
        self.auth_repository.save_storage_state(self.browser_manager.context)
        return locator
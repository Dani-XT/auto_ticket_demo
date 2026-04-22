import logging

from src.automation.browser import BrowserManager
from src.automation.flows.login_flow import LoginFlow
from src.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.auth_repository = AuthRepository()
        self.browser_manager = BrowserManager()

    def start_authenticated_page(self):
        storage_state = None

        if self.auth_repository.exists():
            storage_state = str(self.auth_repository.get_state_path())
            logger.info("Usando sesión guardada")

        page = self.browser_manager.start(storage_state=storage_state)

        login_flow = LoginFlow(page=page, browser_manager=self.browser_manager, auth_repository=self.auth_repository,)

        login_flow.open_home()
        login_flow.wait_for_login()

        return page, self.browser_manager
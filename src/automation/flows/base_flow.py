import logging

from src.automation.waits import (
    wait_in_all_frames,
    smart_click,
    wait_visible_popup,
    get_label_txt,
    deselect_page,
    retry_ui_block,
)

logger = logging.getLogger(__name__)

class BaseFlow:
    def __init__(self, page):
        self.page = page

    def go_home(self):
        try:
            self.page.goto("https://unab.proactivanet.com/proactivanet/servicedesk/default.paw", wait_until="domcontentloaded", timeout=60_000,)
        except Exception:
            logger.exception("No se pudo volver al home.")

    def go_to(self, url: str):
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=60_000,)
        except Exception:
            logger.exception(f"No se pudo dirigir a la pagina {url}")
    
    def _run_step(self, action, error_message: str, attemps: int = 3, step_ms: int = 300):
        return retry_ui_block(page = self.page, action = action, attempts = attemps, step_ms = step_ms, recover = lambda: deselect_page(self.page), error_message = error_message)
    
    def _find_visible(self, selector: str, timeout_ms: int = 10_000, require_enabled: bool = False):
        return wait_in_all_frames(self.page, selector, timeout_ms=timeout_ms, state="visible", require_enabled=require_enabled,)

    def _safe_click(self, selector: str, timeout_ms: int = 10_000, require_enabled: bool = True, expect_nav: bool = False):
        locator, frame = self._find_visible(selector, timeout_ms=timeout_ms, require_enabled=require_enabled,)
        smart_click(locator, frame=frame, expect_nav=expect_nav)
        return locator, frame

    def _get_label(self, selector: str, timeout_ms: int = 10_000) -> str:
        return get_label_txt(self.page, selector=selector, timeout_ms=timeout_ms)

    def _wait_popup(self, popup_selector: str, must_contain_selector: str, timeout_ms: int = 10_000):
        return wait_visible_popup(self.page, popup_selector, must_contain_selector=must_contain_selector, timeout_ms=timeout_ms,)
    
    def go_reload(self):
        self.page.reload(wait_until="domcontentloaded")
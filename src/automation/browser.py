import winreg

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


def get_default_browser() -> str:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice",
        )
        prog_id, _ = winreg.QueryValueEx(key, "ProgId")
        prog_id = prog_id.lower()

        if "chrome" in prog_id:
            return "chrome"
        if "edge" in prog_id:
            return "msedge"
    except Exception:
        pass

    return "chrome"


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def start(self, storage_state: str | None = None) -> Page:
        self.playwright = sync_playwright().start()

        channel = get_default_browser()

        self.browser = self.playwright.chromium.launch(
            channel=channel,
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context_kwargs = {"viewport": None}
        if storage_state:
            context_kwargs["storage_state"] = storage_state

        self.context = self.browser.new_context(**context_kwargs)
        self.page = self.context.new_page()
        return self.page

    def close(self) -> None:
        try:
            if self.context:
                self.context.close()
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
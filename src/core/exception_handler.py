from __future__ import annotations

import logging
import sys
import threading
from tkinter import messagebox


from src.utils.exceptions import AppError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow

logger = logging.getLogger(__name__)

class GlobalExceptionHandler:
    def __init__(self):
        self.root: MainWindow | None = None
        self._default_sys_hook = sys.excepthook
        self._default_thread_hook = getattr(threading, "excepthook", None)

    def install(self, root: MainWindow) -> None:
        self.root = root
        # Errores tkinter
        root.report_callback_exception = self.handle_tk_exception
        # Errores hilo principal
        sys.excepthook = self.handle_sys_exception
        # Errores hilo secundarios
        if hasattr(threading, "excepthook"):
            threading.excepthook = self.handle_thread_exception

    def handle_tk_exception(self, exc_type, exc_value, exc_traceback):
        self._handle(exc_type, exc_value, exc_traceback)

    def handle_sys_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            return self._default_sys_hook(exc_type, exc_value, exc_traceback)

        self._handle(exc_type, exc_value, exc_traceback)

    def handle_thread_exception(self, args):
        try:
            self._handle(args.exc_type, args.exc_value, args.exc_traceback)
        except Exception:
            if self._default_thread_hook is not None:
                self._default_thread_hook(args)

    def _handle(self, exc_type, exc_value, exc_traceback):
        logger.exception("Excepción no controlada", exc_info=(exc_type, exc_value, exc_traceback),)

        if isinstance(exc_value, AppError):
            title = exc_value.title
            message = str(exc_value)
        else:
            title = "Ocurrió un error inesperado"
            message = str(exc_value) or exc_type.__name__

        self._show_error(title, message)

    def _show_error(self, title: str, message: str):
        if self.root and self.root.winfo_exists():
            can_use_custom_ui = (
                hasattr(self.root, "is_ui_ready")
                and callable(self.root.is_ui_ready)
                and self.root.is_ui_ready()
                and hasattr(self.root, "show_global_error")
                and callable(self.root.show_global_error)
            )

            if can_use_custom_ui:
                self.root.after(0, lambda: self.root.show_global_error(title, message))
                return

            self.root.after(0, lambda: messagebox.showerror(title, message, parent=self.root))
            return

        messagebox.showerror(title, message)
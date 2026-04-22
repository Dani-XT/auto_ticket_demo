# Coordinador general de la aplicación y del flujo entre vistas.
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from src.core.app_context import AppContext
from src.models.excel_models import ExcelResult

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow

class AppController:
    def __init__(self, window: MainWindow, app_context: AppContext):
        self.window = window

        self.excel_path: Path | None = None
        self.excel_result: ExcelResult | None = None

        self.app_context = app_context

        self.paths = app_context.paths
        self.config = app_context.config
        self.runtime = app_context.runtime

    def go_to(self, frame_name: str):
        return self.window.show_frame(frame_name)
    
    # -- Agrega resultado y selected file de una --
    def set_excel_context(self, file_path: Path, result: ExcelResult):
        self.excel_path = file_path
        self.excel_result = result
    
    # -- limpieza total --
    def get_excel_context(self):
        return self.excel_path, self.excel_result

    def clear_excel_context(self) -> None:
        self.excel_path = None
        self.excel_result = None
    
    

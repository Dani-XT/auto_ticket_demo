# Gestiona desde la UI todo lo relacionado con cargar, validar y preparar el Excel.
from pathlib import Path
from tkinter import filedialog

from src.controllers.app_controller import AppController

from src.services.excel_service import ExcelService

from src.models.excel_models import ExcelResult


class ExcelController:
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller
        self.excel_service = ExcelService()

    def select_excel_file(self) -> Path | None:
        file_path = filedialog.askopenfilename(
            title="Seleccionar planilla de Excel",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Todos los archivos", "*.*"),
            ]
        )

        if not file_path:
            return None

        return Path(file_path)

    def load_excel(self, excel_path: Path) -> ExcelResult:
        result = self.excel_service.load_jobs(excel_path)
        self.app_controller.set_excel_context(excel_path, result)
        return result
    
    
        


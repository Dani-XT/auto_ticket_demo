import os
from pathlib import Path
import shutil

from tkinter import filedialog

from src.controllers.app_controller import AppController
from src.controllers.excel_controller import ExcelController

from src.controllers.views.process_controller import ProcessController

from src.utils.exceptions import AppError

from src.ui.views.upload_view import UploadView

from src.utils.exceptions import TemplateNotFoundError, HelpFileNotFoundError, HelpFileOpenError

class UploadController:
    def __init__(self, app_controller: AppController, excel_controller: ExcelController, process_controller: ProcessController):
        self.app_controller = app_controller
        self.excel_controller = excel_controller
        self.process_controller = process_controller

        self.paths = self.app_controller.runtime

    def on_download_template(self, view: UploadView):
        saved_path = self._download_template()
        if saved_path:
            view.show_info_message("Descarga exitosa", f"La planilla se guardó correctamente en:\n{saved_path}")
    
    def on_open_help(self):
        self._open_help_file(self.paths.upload_readme_file)

    def on_select_file(self, view: UploadView):
        selected = self.excel_controller.select_excel_file()
        if not selected:
            return

        try:
            result = self.excel_controller.load_excel(selected)
            view.show_selected_file(selected.name)
            view.show_excel_loaded(result.total_jobs)

        except AppError as e:
            self.on_clear_file(view)
            view.show_error_message(e.title, str(e))
            return

    def on_clear_file(self, view: UploadView):
        self.app_controller.clear_excel_context()
        view.clear_selected_file()

    def on_send(self, view:UploadView):
        try:
            process_view = self.app_controller.go_to("process")
            self.process_controller.start(process_view)
        except AppError as e:
            self.app_controller.go_to("upload")
            view.show_error_message(e.title, str(e))

    def on_go_settings(self):
        self.app_controller.go_to("settings")

    def _download_template(self) -> Path | None :
        template_path = self.paths.templates_dir / "Planilla de Actividades - Nombre Tecnico.xlsx"

        if not template_path.exists():
            raise TemplateNotFoundError("No se encontro Plantilla")
        
        save_path = filedialog.asksaveasfilename(
            title="Guardar planilla",
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            initialfile=template_path.name,
        )

        if not save_path:
            return None
        
        shutil.copyfile(template_path, Path(save_path))
        return Path(save_path)
        
    def _open_help_file(self, help_file: Path) -> None:
        if not help_file.exists():
            raise HelpFileNotFoundError("No se encontró el archivo de ayuda.")

        try:
            os.startfile(help_file)
        except Exception as e:
            raise HelpFileOpenError(f"Ocurrió un error al abrir el archivo:\n{e}") from e

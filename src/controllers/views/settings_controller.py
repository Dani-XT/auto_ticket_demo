from src.ui.views.settings_view import SettingsView

from src.controllers.app_controller import AppController

from src.manager.settings_manager import SettingsManager
from src.repositories.auth_repository import AuthRepository

class SettingsController:
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller
        self.settings_manager = SettingsManager()
        self.auth_repository = AuthRepository()

    def on_show(self, view: SettingsView):
        settings = self.settings_manager.get_settings()
        view.set_report_user(settings["report_user"])
        view.set_job_group(settings["job_group"])

    def on_save(self, view: SettingsView):
        report_user = view.get_report_user()
        job_group = view.get_job_group()

        self.settings_manager.save_settings(report_user.strip(), job_group.strip())
        view.show_info_message("Configuración guardada", "Los cambios se guardaron correctamente.")

    def on_restore_defaults(self, view: SettingsView):
        self.settings_manager.restore_defaults()
        self.on_show(view)
        view.show_info_message("Configuración restaurada", "Se restauraron los valores por defecto.")

    def on_delete_session(self, view: SettingsView):
        if not self.auth_repository.exists():
            view.show_warning_message(
                "Sesión no encontrada",
                "No existe una sesión guardada para eliminar."
            )
            return

        self.auth_repository.delete()
        view.show_info_message(
            "Sesión eliminada",
            "La sesión guardada fue eliminada correctamente. La próxima vez deberás iniciar sesión nuevamente."
        )


    def on_back(self):
        self.app_controller.go_to("upload")

    

import logging
import tkinter as tk
import ctypes

# Controllers del negocio
from src.controllers.app_controller import AppController
from src.controllers.excel_controller import ExcelController
from src.controllers.automation_controller import AutomationController

# Controller de las view
from src.controllers.views.upload_controller import UploadController
from src.controllers.views.process_controller import ProcessController
from src.controllers.views.settings_controller import SettingsController

# Frames del sistema
from src.ui.frames.process_frame import ProcessFrame
from src.ui.frames.upload_frame import UploadFrame
from src.ui.frames.settings_frame import SettingsFrame

from src.ui.components.dialogs import show_error

from src.core.app_context import AppContext

logger = logging.getLogger(__name__)

class MainWindow(tk.Tk):
    def __init__(self, app_context: AppContext):
        super().__init__()

        self.app_context = app_context

        self.config = app_context.config
        self.paths = app_context.paths
        
        self._configure_window()
        self._load_task_icon()

        self.current_frame = None
        self.ui_ready = False

        # Controllers Negocio
        self.app_controller = AppController(self, app_context)
        self.excel_controller = ExcelController(self.app_controller)
        self.automation_controller = AutomationController()
        
        # Controllers Views
        self.process_controller = ProcessController(self.app_controller, self.automation_controller)
        self.upload_controller = UploadController(self.app_controller, self.excel_controller, self.process_controller)
        self.settings_controller = SettingsController(self.app_controller)
        
        self.container = tk.Frame(self, bg="#E91A1D")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self._build_frames()
        self.show_frame("upload")

        self.ui_ready = True

    def _configure_window(self):
        self.title(self.config.app_title)
        self.geometry(self.config.app_size)
        self.resizable(False, False)

    def _load_task_icon(self):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.config.app_id)
        except Exception:
            pass

        try:
            self.iconbitmap(str(self.paths.icon_dir / "favicon.ico"))
        except Exception:
            pass

    def _build_frames(self):
        self.frames["process"] = ProcessFrame(self.container, self.app_context, self.process_controller) # UI Progreso
        self.frames["upload"] = UploadFrame(self.container, self.app_context, self.upload_controller) # Cargar ticket
        self.frames["settings"] = SettingsFrame(self.container, self.app_context, self.settings_controller) # Configuraciones

        for frame in self.frames.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_frame(self, name: str):
        self.current_frame = self.frames[name]
        self.current_frame.tkraise()
        return self.current_frame

    def is_ui_ready(self) -> bool:
        return self.ui_ready and self.winfo_exists()
    
    def show_global_error(self, title: str, message: str):
        if self.current_frame is not None and self.current_frame.winfo_exists():
            self.current_frame.show_error_message(title, message)
        else:
            show_error(self, title, message)


import tkinter as tk

from src.core.app_context import AppContext

from src.ui.components.dialogs import show_info, show_error, show_warning

class BaseFrame(tk.Frame):

    def __init__(self, master, context: AppContext, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.context = context

        self.paths = context.paths

        self.logo_img = tk.PhotoImage(file = self.paths.img_dir / "logo.png")
        
    def show_info_message(self, title: str, message: str):
        show_info(self, title, message)

    def show_error_message(self, title: str, message: str):
        show_error(self, title, message)

    def show_warning_message(self, title: str, message: str):
        show_warning(self, title, message)


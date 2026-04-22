import tkinter as tk
from tkinter import messagebox

from src.app.bootstrap import bootstrap_app
from src.ui.main_window import MainWindow
from src.core.exception_handler import GlobalExceptionHandler

def show_startup_error(title: str, message: str):
    root = tk.Tk()
    root.withdraw()
    try:
        messagebox.showerror(title, message, parent=root)
    finally:
        root.destroy()

def build_app() -> MainWindow:
    app_context = bootstrap_app()
    app = MainWindow(app_context)

    exception_handler = GlobalExceptionHandler()
    exception_handler.install(app)

    return app

def main():
    try:
        app = build_app()
    except Exception as e:
        show_startup_error("Ocurrio un error inesperado", str(e))
        return
        
    app.mainloop()

if __name__ == "__main__":
    main()
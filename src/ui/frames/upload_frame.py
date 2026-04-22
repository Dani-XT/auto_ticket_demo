import tkinter as tk
from PIL import Image, ImageTk

from src.ui.frames.base_frame import BaseFrame

from src.controllers.views.upload_controller import UploadController

from src.core.app_context import AppContext

from src.ui.components.tooltip import Tooltip
from src.ui.components.dialogs import show_info

class UploadFrame(BaseFrame):
    def __init__(self, master, context: AppContext, page_controller: UploadController):
        super().__init__(master, context, bg="#E91A1D")
        
        self.controller = page_controller

        self._load_assets()
        self._build_header()
        self._build_body()
        self._build_footer()

    def _load_assets(self):
        frame_img_dir = self.paths.img_dir / "upload_frame"

        excel_image = Image.open(frame_img_dir / "excel.png")
        excel_image = excel_image.resize((40, 40), Image.LANCZOS)
        self.excel_img = ImageTk.PhotoImage(excel_image)

        self.input_img = tk.PhotoImage(file=frame_img_dir / "input_file.png")
        self.help_img = tk.PhotoImage(file=frame_img_dir / "helper.png")
        self.config_img = tk.PhotoImage(file=frame_img_dir / "configuracion.png")
        self.convert_img = tk.PhotoImage(file=frame_img_dir / "convertir.png")
        self.send_img = tk.PhotoImage(file=frame_img_dir / "enviar.png")
        self.clear_img = tk.PhotoImage(file=frame_img_dir / "close.png")

    def _build_header(self):
        header = tk.Frame(self, bg="#E91A1D")
        header.place(x=42, y=30)

        logo_label = tk.Label(header, image=self.logo_img, bg="#E91A1D")
        logo_label.pack(side="left")

        title_label = tk.Label(header, text="Carga Automatica de Ticket", font=("Segoe UI", 18, "bold"), fg="white", bg="#E91A1D",)
        title_label.pack(side="left", padx=38)

        excel_btn = tk.Button(header, image=self.excel_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command=lambda: self.controller.on_download_template(self), cursor="hand2",)
        excel_btn.pack(side="left", padx=5)

        Tooltip(excel_btn, "Descargar Planilla")

    def _build_body(self):
        tk.Label(self, text="Cargar Planilla", font=("Segoe UI", 12, "bold"), fg="white", bg="#E91A1D",).place(x=40, y=140)

        help_btn = tk.Button(self, image=self.help_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command= self.controller.on_open_help, cursor="hand2",)
        help_btn.place(x=165, y=140)
        Tooltip(help_btn, "Ayuda")

        input_btn = tk.Button(self, image=self.input_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command=lambda: self.controller.on_select_file(self) , cursor="hand2",)
        input_btn.place(x=40, y=170)
        Tooltip(input_btn, "Cargar planilla")

        self.file_container = tk.Frame(self, bg="#FDF7F7")
        self.file_label = tk.Label(self.file_container, text="", font=("Segoe UI", 12, "bold"), fg="#333333", bg="#FDF7F7",anchor="w",)
        self.file_label.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.clear_btn = tk.Button(self.file_container, image=self.clear_img, bg="#FDF7F7", activebackground="#FDF7F7", borderwidth=0, command=lambda: self.controller.on_clear_file(self), cursor="hand2",)
        self.clear_btn.pack(side="right", padx=5)

    def _build_footer(self):
        footer = tk.Frame(self, bg="#E91A1D")
        footer.place(relx=0.5, y=300, anchor="center")

        config_btn = tk.Button(footer, image=self.config_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command= self.controller.on_go_settings, cursor="hand2",)
        config_btn.pack(side="left", padx=15)

        send_btn = tk.Button(footer, image=self.send_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command=lambda: self.controller.on_send(self), cursor="hand2",)
        send_btn.pack(side="left", padx=15)


    def show_selected_file(self, file_name: str):
        self.file_label.config(text=file_name)
        self.file_container.place(x=55, y=180, width=480, height=24)

    def clear_selected_file(self):
        self.file_label.config(text="")
        self.file_container.place_forget()

    def show_excel_loaded(self, total_jobs: int):
        show_info(self, "Planilla cargada", f"Se detectaron {total_jobs} ticket(s) pendientes para procesar.")


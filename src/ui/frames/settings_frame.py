import tkinter as tk

from src.ui.frames.base_frame import BaseFrame

from src.core.app_context import AppContext

from src.controllers.views.settings_controller import SettingsController

class SettingsFrame(BaseFrame):
    def __init__(self, master, context: AppContext, page_controller: SettingsController):
        super().__init__(master, context, bg="#E91A1D")

        self.controller = page_controller

        self._load_assets()
        self._build_header()
        self._build_body()
        self._build_footer()

        self.controller.on_show(self)
        
    def _load_assets(self):
        frame_img_dir = self.paths.img_dir / "settings_frame"

        self.input_img = tk.PhotoImage(file = frame_img_dir / "input.png")
        self.save_img = tk.PhotoImage(file = frame_img_dir / "guardar.png")
        self.restore_img = tk.PhotoImage(file = frame_img_dir / "restaurar.png")
        self.back_img = tk.PhotoImage(file = frame_img_dir / "volver.png")
        self.delete_img = tk.PhotoImage(file = frame_img_dir / "borrar_sesion.png")

    def _build_header(self):
        header = tk.Frame(self, bg="#E91A1D")
        header.place(x=42, y=30)

        logo_label = tk.Label(header, image=self.logo_img, bg="#E91A1D")
        logo_label.pack(side="left")

        title_label = tk.Label(header, text="Configuracion", font=("Segoe UI", 18, "bold"), fg="white", bg="#E91A1D")
        title_label.pack(side="left", padx=100)
    
    def _build_body(self):
        
        tk.Label(self, text="Usuario Reportante", font=("Segoe UI", 12, "bold"), fg="white", bg="#E91A1D").place(x=46, y=117)

        tk.Label(self, text="Grupo de Trabajo", font=("Segoe UI", 12, "bold"), fg="white", bg="#E91A1D").place(x=46, y=196)
        
        tk.Label(self, image=self.input_img, bg="#E91A1D", borderwidth=0).place(x=40, y=142)
        self.report_user_entry = tk.Entry(self, width=35, font=("Segoe UI", 11), fg="#333333", bg="white", relief="flat", highlightthickness=0, insertbackground="#333333", justify="left")
        self.report_user_entry.place(x=50, y=151)

        tk.Label(self, image=self.input_img, bg="#E91A1D", borderwidth=0).place(x=40, y=221)
        self.job_group_entry = tk.Entry(self, width=35, font=("Segoe UI", 11), fg="#333333", bg="white", relief="flat", highlightthickness=0, insertbackground="#333333", justify="left")
        self.job_group_entry.place(x=50, y=231)

    def _build_footer(self):
        footer = tk.Frame(self, bg="#E91A1D")
        footer.place(relx=0.5, y=310, anchor="center")


        back_btn = tk.Button(footer, image=self.back_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command=self.controller.on_back, cursor="hand2")
        back_btn.pack(side="left", padx=6)

        restore_btn = tk.Button(footer, image=self.restore_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command=lambda: self.controller.on_restore_defaults(self), cursor="hand2")
        restore_btn.pack(side="left", padx=6)

        delete_btn = tk.Button(footer, image=self.delete_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command=lambda: self.controller.on_delete_session(self), cursor="hand2")
        delete_btn.pack(side="left", padx=6)

        save_btn = tk.Button(footer, image=self.save_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command=lambda: self.controller.on_save(self), cursor="hand2")
        save_btn.pack(side="left", padx=6)

    def get_report_user(self) -> str:
        return self.report_user_entry.get()

    def get_job_group(self) -> str:
        return self.job_group_entry.get()

    def set_report_user(self, value: str) -> None:
        self.report_user_entry.delete(0, tk.END)
        self.report_user_entry.insert(0, value)

    def set_job_group(self, value: str) -> None:
        self.job_group_entry.delete(0, tk.END)
        self.job_group_entry.insert(0, value)

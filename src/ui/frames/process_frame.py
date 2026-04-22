import tkinter as tk
from tkinter import ttk

from src.ui.frames.base_frame import BaseFrame
from src.ui.components.dialogs import show_info

from src.core.app_context import AppContext

from src.controllers.views.process_controller import ProcessController

class ProcessFrame(BaseFrame):
    def __init__(self, master, context: AppContext, page_controller: ProcessController):
        super().__init__(master, context, bg="#E91A1D")

        self.controller = page_controller
        self._job_items: dict[int, str] = {}

        self._load_assets()

        self._build_header()
        self._build_body()
        self._build_footer()


    def _load_assets(self):
        frame_img_dir = self.paths.img_dir / "process_frame"
        self.back_img = tk.PhotoImage(file=frame_img_dir / "volver.png")
        
    def _build_header(self) -> None:
        header = tk.Frame(self, bg="#E91A1D")
        header.place(x=42, y=10)

        logo_label = tk.Label(header, image=self.logo_img, bg="#E91A1D")
        logo_label.pack(side="left")

        title_label = tk.Label(header, text="Procesamiento", font=("Segoe UI", 18, "bold"), fg="white", bg="#E91A1D",)
        title_label.pack(side="left", padx=90)

    def _build_body(self) -> None:
        tk.Label(self, text="Estado del proceso", font=("Segoe UI", 12, "bold"), fg="white", bg="#E91A1D",).place(x=40, y=90)

        self.status_card = tk.Frame(self, bg="#FDF7F7", highlightthickness=0, bd=0)
        self.status_card.place(x=40, y=115, width=557, height=34)

        self.status_label = tk.Label(self.status_card, text="Esperando inicio...", font=("Segoe UI", 10, "bold"), fg="#333333",bg="#FDF7F7", anchor="w",)
        self.status_label.pack(fill="both", expand=True, padx=10)

        tk.Label(self, text="Detalle por fila", font=("Segoe UI", 12, "bold"), fg="white", bg="#E91A1D",).place(x=40, y=155)

        table_container = tk.Frame(self, bg="#FDF7F7")
        table_container.place(x=40, y=190, width=557, height=115)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Process.Treeview", background="#FFFFFF", foreground="#333333", fieldbackground="#FFFFFF", rowheight=22, borderwidth=0, font=("Segoe UI", 9),)
        style.configure("Process.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#F3F3F3", foreground="#333333", relief="flat",)

        self.table = ttk.Treeview(table_container, columns=("fila", "estado", "ticket", "error"), show="headings", style="Process.Treeview",)

        self.table.heading("fila", text="Fila")
        self.table.heading("estado", text="Estado")
        self.table.heading("ticket", text="Ticket")
        self.table.heading("error", text="Error")

        self.table.column("fila", width=55, minwidth=55, anchor="center", stretch=False)
        self.table.column("estado", width=125, minwidth=125, anchor="center", stretch=False)
        self.table.column("ticket", width=95, minwidth=95, anchor="center", stretch=False)
        self.table.column("error", width=260, minwidth=260, anchor="w", stretch=True)

        y_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=y_scroll.set)

        self.table.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg="#E91A1D")
        footer.place(relx=0.5, y=335, anchor="center")


        self.back_button = tk.Button(footer, image=self.back_img, bg="#E91A1D", activebackground="#E91A1D", borderwidth=0, command= self.controller.on_back, cursor="hand2",)
        self.back_button.pack()

    def reset_view(self) -> None:
        self.status_label.config(text="Esperando inicio...")
        
        self._job_items.clear()

        for item in self.table.get_children():
            self.table.delete(item)

    def set_status(self, message: str) -> None:
        self.status_label.config(text=message)
        self.update_idletasks()

    def load_jobs(self, jobs) -> None:
        self.reset_view()

        for job in jobs:
            item_id = self.table.insert(
                "", 
                "end",
                values=(
                    job.row_id,
                    job.status.value,
                    job.ticket_id or "",
                    job.error or "",
                ),
            )
            self._job_items[job.row_id] = item_id

    def update_job_status(self, row_id: int, status: str, ticket_id: str | None, error: str | None,) -> None:
        item_id = self._job_items.get(row_id)
        if not item_id:
            return

        self.table.item(
            item_id,
            values=(
                row_id,
                status,
                ticket_id or "",
                error or "",
            ),
        )
        self.update_idletasks()

    def show_completed(self, message: str) -> None:
        show_info(self, "Proceso finalizado", message)
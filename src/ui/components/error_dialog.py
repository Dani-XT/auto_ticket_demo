import tkinter as tk
from PIL import Image, ImageTk

from src.app.paths import ICON_DIR, IMG_DIR


class ErrorDialog(tk.Toplevel):
    def __init__(self, master, title: str, message: str, level: str = "error"):
        super().__init__(master)

        self.withdraw()  

        self.title(title)
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        try:
            self.iconbitmap(str(self._load_img(level, icon=True)))
        except Exception:
            pass

        self._build_ui(message, level)

        self.transient(master)
        self.grab_set()
        self.update_idletasks()

        # centra el parent
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_reqwidth() // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_reqheight() // 2)
        self.geometry(f"+{x}+{y}")

        self.deiconify()   # mostrar ya armado
        self.focus_force()

    def _load_img(self, level: str, icon: bool = True):
        if icon:
            icon_map = {
                "error": "error.ico",
                "warning": "warning.ico",
                "info": "info.ico",
            }
            return ICON_DIR / icon_map.get(level, "error.ico")

        image_map = {
            "error": "error.png",
            "warning": "warning.png",
            "info": "info.png",
        }
        return IMG_DIR / image_map.get(level, "error.png")

    def _build_ui(self, message: str, level: str):
        color = {
            "error": "#E53935",
            "warning": "#FB8C00",
            "info": "#1E88E5",
        }.get(level, "#E53935")

        container = tk.Frame(self, bg="#1e1e1e")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        img_path = self._load_img(level, icon=False)
        img = Image.open(img_path)
        img = img.resize((48, 48), Image.LANCZOS)

        self.img = ImageTk.PhotoImage(img)

        tk.Label(container, image=self.img, bg="#1e1e1e").grid(row=0, column=0, padx=(0, 15), sticky="n")
        tk.Label(container, text=message, bg="#1e1e1e", fg="white", wraplength=360, font=("Segoe UI", 11), justify="left").grid(row=0, column=1, sticky="w")
        tk.Button(self, text="Cerrar", bg=color, fg="white", relief="flat", command=self.destroy).pack(pady=(0, 15))
import tkinter as tk
from tkinter import ttk, messagebox
import src.backend as backend

class VentanaConfiguracion:
    def __init__(self, parent, callback_actualizar):
        self.parent = parent
        self.callback_actualizar = callback_actualizar
        
        self.win = tk.Toplevel(parent)
        self.win.title("Configuración de rutas (.ini)")
        self.win.geometry("480x300")
        self.win.grab_set()
        self.win.resizable(False, False)

        self.config = backend.cargar_configuracion()
        self.crear_componentes()

    def crear_componentes(self):
        frame = ttk.Frame(self.win, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        self.vl_r_lin = tk.StringVar(value=self.config['ruta_linux'])
        self.vl_p_lin = tk.StringVar(value=self.config['prefijo_linux'])
        self.vl_r_mac = tk.StringVar(value=self.config['ruta_macos'])
        self.vl_p_mac = tk.StringVar(value=self.config['prefijo_macos'])

        # Sección Linux
        ttk.Label(frame, text="Linux - Ruta Base:", font=('Helvetica', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.vl_r_lin, width=30).grid(row=0, column=1, pady=2, padx=5)
        ttk.Label(frame, text="Linux - Prefijo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.vl_p_lin, width=30).grid(row=1, column=1, pady=2, padx=5)

        ttk.Separator(frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        # Sección macOS
        ttk.Label(frame, text="macOS - Ruta Base:", font=('Helvetica', 9, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.vl_r_mac, width=30).grid(row=3, column=1, pady=2, padx=5)
        ttk.Label(frame, text="macOS - Prefijo:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.vl_p_mac, width=30).grid(row=4, column=1, pady=2, padx=5)

        ttk.Button(frame, text="Guardar Configuración", command=self.guardar).grid(row=5, column=0, columnspan=2, sticky="ew", pady=15)

    def guardar(self):
        backend.guardar_configuracion(
            self.vl_r_lin.get().strip(), self.vl_p_lin.get().strip(),
            self.vl_r_mac.get().strip(), self.vl_p_mac.get().strip()
        )
        self.callback_actualizar()
        messagebox.showinfo("Éxito", "Configuración actualizada correctamente.", parent=self.win)
        self.win.destroy()

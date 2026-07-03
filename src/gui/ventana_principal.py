import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import src.backend as backend
from src.gui.ventana_config import VentanaConfiguracion

class AppM3UMigrator:
    def __init__(self, root):
        self.root = root
        self.root.title("Migrador de Listas M3U (Multi-Sistema)")
        self.root.geometry("600x380")
        self.root.resizable(False, False)
        try:
            # Calculamos la ruta hacia src/assets/icon.png desde este archivo
            base_dir = os.path.dirname(os.path.dirname(__file__)) # Sube a la carpeta 'src'
            ruta_icono = os.path.join(base_dir, 'assets', 'icon.png')
            
            if os.path.exists(ruta_icono):
                # Cargamos la imagen y la asignamos a la ventana
                self.icono_app = tk.PhotoImage(file=ruta_icono)
                self.root.iconphoto(False, self.icono_app)
        except Exception as e:
            print(f"No se pudo cargar el icono visual: {e}")
        self.ruta_origen = tk.StringVar()
        self.nombre_destino = tk.StringVar()
        self.sistema_objetivo = tk.StringVar(value="Linux")
        
        self.config = backend.cargar_configuracion()

        self.crear_menu()
        self.crear_interfaz()

    def crear_menu(self):
        barra_menu = tk.Menu(self.root)
        menu_config = tk.Menu(barra_menu, tearoff=0)
        menu_config.add_command(label="Modificar Configuración (.ini)", command=self.abrir_configuracion)
        menu_config.add_separator()
        menu_config.add_command(label="Salir", command=self.root.quit)
        barra_menu.add_cascade(label="Archivo", menu=menu_config)
        self.root.config(menu=barra_menu)

    def crear_interfaz(self):
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Origen
        ttk.Label(frame, text="Lista de reproducción origen (Windows):", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        frame_origen = ttk.Frame(frame)
        frame_origen.pack(fill=tk.X, pady=(0, 10))
        entry_origen = ttk.Entry(frame_origen, textvariable=self.ruta_origen, state='readonly')
        entry_origen.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(frame_origen, text="Buscar...", command=self.seleccionar_archivo).pack(side=tk.RIGHT)

        # Combo Sistema
        ttk.Label(frame, text="Sistema operativo destino:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.combo_sistema = ttk.Combobox(frame, textvariable=self.sistema_objetivo, values=["Linux", "macOS"], state="readonly")
        self.combo_sistema.pack(fill=tk.X, pady=(0, 10))
        self.combo_sistema.bind("<<ComboboxSelected>>", self.actualizar_UI)

        # Destino
        ttk.Label(frame, text="Nombre del archivo resultante:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(frame, textvariable=self.nombre_destino).pack(fill=tk.X, pady=(0, 15))

        # Procesar
        self.btn_procesar = ttk.Button(frame, text="Migrar Lista de Reproducción", command=self.ejecutar, state=tk.DISABLED)
        self.btn_procesar.pack(fill=tk.X, ipady=8)

        # Info footer
        self.lbl_info = ttk.Label(frame, text="", font=('Helvetica', 9, 'italic'), foreground="gray")
        self.lbl_info.pack(anchor=tk.W, pady=(15, 0))
        self.actualizar_UI()

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(title="Seleccionar Lista", filetypes=[("Listas M3U/M3U8", "*.m3u *.m3u8")])
        if archivo:
            self.ruta_origen.set(archivo)
            self.actualizar_UI()
            self.btn_procesar.config(state=tk.NORMAL)

    def actualizar_UI(self, event=None):
        self.config = backend.cargar_configuracion()
        if self.ruta_origen.get():
            nombre_base = os.path.basename(self.ruta_origen.get())
            prefijo = self.config['prefijo_linux'] if self.sistema_objetivo.get() == "Linux" else self.config['prefijo_macos']
            self.nombre_destino.set(prefijo + nombre_base)
        
        ruta_txt = self.config['ruta_linux'] if self.sistema_objetivo.get() == "Linux" else self.config['ruta_macos']
        self.lbl_info.config(text=f"Ruta {self.sistema_objetivo.get()} activa en el .ini: {ruta_txt}")

    def abrir_configuracion(self):
        VentanaConfiguracion(self.root, self.actualizar_UI)

    def ejecutar(self):
        origen = self.ruta_origen.get()
        destino_completo = os.path.join(os.path.dirname(origen), self.nombre_destino.get())
        ruta_base = self.config['ruta_linux'] if self.sistema_objetivo.get() == "Linux" else self.config['ruta_macos']

        try:
            canciones = backend.procesar_playlist(origen, ruta_base, destino_completo)
            messagebox.showinfo("Éxito", f"Lista exportada para {self.sistema_objetivo.get()}.\nProcesadas {canciones} canciones.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar:\n{str(e)}")

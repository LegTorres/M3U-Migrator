import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import src.backend as backend
from src.gui.ventana_config import VentanaConfiguracion

class AppM3UMigrator:
    def __init__(self, root):
        self.root = root
        self.root.title("Migrador de Listas M3U (Multi-Sistema)")
        self.root.geometry("600x420") # Aumentamos un poco el alto para el nuevo campo
        self.root.resizable(False, False)

        # Asignar icono de la aplicación
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            ruta_icono = os.path.join(base_dir, 'assets', 'icono.png')
            if os.path.exists(ruta_icono):
                self.icono_app = tk.PhotoImage(file=ruta_icono)
                self.root.iconphoto(False, self.icono_app)
        except Exception as e:
            print(f"No se pudo cargar el icono visual: {e}")

        # Variables de control
        self.ruta_origen = tk.StringVar()
        self.ruta_destino = tk.StringVar() # Almacena la ruta absoluta completa final
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

        # --- SECCIÓN: ARCHIVO ORIGEN ---
        ttk.Label(frame, text="Lista de reproducción origen (Windows):", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        frame_origen = ttk.Frame(frame)
        frame_origen.pack(fill=tk.X, pady=(0, 10))
        entry_origen = ttk.Entry(frame_origen, textvariable=self.ruta_origen, state='readonly')
        entry_origen.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(frame_origen, text="Buscar...", command=self.seleccionar_archivo_origen).pack(side=tk.RIGHT)

        # --- SECCIÓN: SISTEMA OBJETIVO ---
        ttk.Label(frame, text="Sistema operativo destino:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.combo_sistema = ttk.Combobox(frame, textvariable=self.sistema_objetivo, values=["Linux", "macOS"], state="readonly")
        self.combo_sistema.pack(fill=tk.X, pady=(0, 10))
        self.combo_sistema.bind("<<ComboboxSelected>>", self.cambio_sistema_operativo)

        # --- SECCIÓN: ARCHIVO DESTINO (NUEVA) ---
        ttk.Label(frame, text="Ubicación y nombre del archivo resultante:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        frame_destino = ttk.Frame(frame)
        frame_destino.pack(fill=tk.X, pady=(0, 20))
        entry_destino = ttk.Entry(frame_destino, textvariable=self.ruta_destino, state='readonly')
        entry_destino.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.btn_guardar_como = ttk.Button(frame_destino, text="Guardar como...", command=self.seleccionar_ubicacion_destino, state=tk.DISABLED)
        self.btn_guardar_como.pack(side=tk.RIGHT)

        # --- BOTÓN DE PROCESAMIENTO ---
        self.btn_procesar = ttk.Button(frame, text="Migrar Lista de Reproducción", command=self.ejecutar, state=tk.DISABLED)
        self.btn_procesar.pack(fill=tk.X, ipady=8)

        # --- INFO FOOTER ---
        self.lbl_info = ttk.Label(frame, text="", font=('Helvetica', 9, 'italic'), foreground="gray")
        self.lbl_info.pack(anchor=tk.W, pady=(15, 0))
        self.actualizar_label_info()

    def seleccionar_archivo_origen(self):
        archivo = filedialog.askopenfilename(title="Seleccionar Lista", filetypes=[("Listas M3U/M3U8", "*.m3u *.m3u8")])
        if archivo:
            self.ruta_origen.set(archivo)

            # Calcular ruta destino sugerida por defecto (misma carpeta del archivo original + prefijo)
            dir_origen = os.path.dirname(archivo)
            nombre_base = os.path.basename(archivo)
            prefijo = self.config['prefijo_linux'] if self.sistema_objetivo.get() == "Linux" else self.config['prefijo_macos']

            self.ruta_destino.set(os.path.join(dir_origen, prefijo + nombre_base))

            # Habilitar botones dependientes
            self.btn_guardar_como.config(state=tk.NORMAL)
            self.btn_procesar.config(state=tk.NORMAL)

    def seleccionar_ubicacion_destino(self):
        """Abre un cuadro de diálogo para cambiar libremente el nombre o la carpeta de salida."""
        if not self.ruta_destino.get():
            return

        nombre_sugerido = os.path.basename(self.ruta_destino.get())
        dir_sugerido = os.path.dirname(self.ruta_destino.get())

        archivo_salida = filedialog.asksaveasfilename(
            title="Seleccionar dónde guardar la lista convertida",
            initialdir=dir_sugerido,
            initialfile=nombre_sugerido,
            filetypes=[("Listas M3U/M3U8", "*.m3u *.m3u8")]
        )

        if archivo_salida:
            self.ruta_destino.set(archivo_salida)

    def cambio_sistema_operativo(self, event=None):
        """Si el usuario cambia el sistema, recalculamos el prefijo del archivo sin perder la carpeta elegida."""
        self.config = backend.cargar_configuracion()
        if self.ruta_destino.get():
            # Extraemos la carpeta actual y el nombre limpio
            dir_actual = os.path.dirname(self.ruta_destino.get())
            nombre_actual = os.path.basename(self.ruta_destino.get())

            # Quitamos el prefijo viejo si existía para no acumularlos (ej: Linux_PL_macOS_PL_rock.m3u)
            if nombre_actual.startswith(self.config['prefijo_linux']):
                nombre_actual = nombre_actual.replace(self.config['prefijo_linux'], "", 1)
            elif nombre_actual.startswith(self.config['prefijo_macos']):
                nombre_actual = nombre_actual.replace(self.config['prefijo_macos'], "", 1)

            # Aplicamos el nuevo prefijo
            prefijo = self.config['prefijo_linux'] if self.sistema_objetivo.get() == "Linux" else self.config['prefijo_macos']
            self.ruta_destino.set(os.path.join(dir_actual, prefijo + nombre_actual))

        self.actualizar_label_info()

    def actualizar_label_info(self):
        ruta_txt = self.config['ruta_linux'] if self.sistema_objetivo.get() == "Linux" else self.config['ruta_macos']
        self.lbl_info.config(text=f"Ruta {self.sistema_objetivo.get()} activa en el .ini: {ruta_txt}")

    def abrir_configuracion(self):
        # Al cerrar la ventana de configuración, refrescamos la UI
        VentanaConfiguracion(self.root, self.cambio_sistema_operativo)

    def ejecutar(self):
        origen = self.ruta_origen.get()
        destino = self.ruta_destino.get()
        ruta_base = self.config['ruta_linux'] if self.sistema_objetivo.get() == "Linux" else self.config['ruta_macos']

        try:
            canciones = backend.procesar_playlist(origen, ruta_base, destino)
            messagebox.showinfo(
                "Éxito",
                f"Lista exportada correctamente para {self.sistema_objetivo.get()}.\n\n"
                f"Guardada en:\n{destino}\n\n"
                f"Procesadas {canciones} canciones."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar:\n{str(e)}")

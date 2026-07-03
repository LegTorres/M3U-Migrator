#!/usr/bin/env python3
import sys
import os

# Añadimos la raíz del proyecto al path para asegurar que las importaciones funcionen desde cualquier lugar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from src.gui.ventana_principal import AppM3UMigrator

def main():
    root = tk.Tk()
    app = AppM3UMigrator(root)
    root.mainloop()

if __name__ == '__main__':
    main()

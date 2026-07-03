import os
import configparser

CONFIG_FILE = 'config.ini'

def obtener_config_defecto():
    # 1. Obtener la ruta del HOME del usuario de forma segura
    home = os.path.expanduser('~')
    
    # 2. Detectar si existe la carpeta en inglés o español para Linux
    if os.path.isdir(os.path.join(home, 'Music')):
        ruta_linux = os.path.join(home, 'Music')
    else:
        ruta_linux = os.path.join(home, 'Musica')
        
    # 3. Detectar si existe la carpeta en inglés o español para macOS
    if os.path.isdir(os.path.join(home, 'Music')):
        ruta_macos = os.path.join(home, 'Music')
    else:
        ruta_macos = os.path.join(home, 'Musica')
    
    return {
        'ruta_linux': ruta_linux,
        'prefijo_linux': 'Linux_PL_',
        'ruta_macos': ruta_macos,
        'prefijo_macos': 'macOS_PL_'
    }

def guardar_configuracion(r_linux, p_linux, r_macos, p_macos):
    config = configparser.ConfigParser()
    config['LECTOR_M3U'] = {
        'ruta_linux': r_linux,
        'prefijo_linux': p_linux,
        'ruta_macos': r_macos,
        'prefijo_macos': p_macos
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)

def cargar_configuracion():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        d = obtener_config_defecto()
        guardar_configuracion(d['ruta_linux'], d['prefijo_linux'], d['ruta_macos'], d['prefijo_macos'])
        return d
    
    config.read(CONFIG_FILE, encoding='utf-8')
    try:
        return {
            'ruta_linux': config['LECTOR_M3U']['ruta_linux'],
            'prefijo_linux': config['LECTOR_M3U']['prefijo_linux'],
            'ruta_macos': config['LECTOR_M3U']['ruta_macos'],
            'prefijo_macos': config['LECTOR_M3U']['prefijo_macos']
        }
    except KeyError:
        return obtener_config_defecto()

def procesar_playlist(archivo_origen, nueva_ruta, archivo_destino):
    with open(archivo_origen, "r", encoding='utf-8') as f:
        contenido = f.read()

    lineas = contenido.split('\n')
    lineas_procesadas = 0

    with open(archivo_destino, 'w', encoding='utf-8') as nuevo_archivo:
        nuevo_archivo.write('#EXTM3U\n')

        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue

            if linea[0] != '#':
                carpetas = linea.split("\\")
                carpetas[0] = nueva_ruta
                # os.path.join maneja de forma nativa las barras '/' de Unix
                nueva_linea = os.path.join(*carpetas)
                nuevo_archivo.write(nueva_linea + '\n')
                lineas_procesadas += 1

    return lineas_procesadas

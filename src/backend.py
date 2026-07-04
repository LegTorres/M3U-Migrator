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
        ruta_linux = os.path.join(home, 'Música')

    # 3. Detectar si existe la carpeta en inglés o español para macOS
    if os.path.isdir(os.path.join(home, 'Music')):
        ruta_macos = os.path.join(home, 'Music')
    else:
        ruta_macos = os.path.join(home, 'Música')

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

def guardar_ruta_musica(sistema, nueva_ruta):
    """Guarda únicamente la ruta seleccionada en el archivo config.ini sin alterar los prefijos."""
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
    else:
        d = obtener_config_defecto()
        config['LECTOR_M3U'] = {
            'ruta_linux': d['ruta_linux'],
            'prefijo_linux': d['prefijo_linux'],
            'ruta_macos': d['ruta_macos'],
            'prefijo_macos': d['prefijo_macos']
        }

    if 'LECTOR_M3U' not in config:
        config['LECTOR_M3U'] = {}

    if sistema == "Linux":
        config['LECTOR_M3U']['ruta_linux'] = nueva_ruta
    elif sistema == "macOS":
        config['LECTOR_M3U']['ruta_macos'] = nueva_ruta

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)

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

            # Saltamos las líneas de metadatos del M3U
            if linea.startswith('#'):
                continue

            # 1. Normalizamos las barras: convertimos todo a barras invertidas de Windows
            linea_normalizada = linea.replace('/', '\\')

            # 2. Separamos la ruta en una lista de carpetas y filtramos elementos vacíos
            carpetas = [c.strip() for c in linea_normalizada.split('\\') if c.strip()]

            # 3. Buscamos dónde termina la ruta base de Windows.
            # Buscaremos la última aparición de palabras clave para cortar a partir de ahí.
            indice_corte = -1
            for i, carp in enumerate(carpetas):
                if carp.lower() in ["music", "música", "musica"]:
                    indice_corte = i

            # 4. Si encontramos "Music", tomamos todo lo que está DESPUÉS de esa carpeta.
            # Si NO la encontramos (o si era el último elemento), asumimos que las últimas
            # 2 o 3 carpetas son el artista/canción (ej: Artista\Álbum\Canción.mp3 o Artista\Canción.mp3)
            if indice_corte != -1 and indice_corte < len(carpetas) - 1:
                partes_musica = carpetas[indice_corte + 1:]
            else:
                # Si no hay palabra clave, nos quedamos de forma segura con los últimos 2 elementos
                # (generalmente Artista y Canción) para evitar arrastrar rutas viejas de Windows.
                partes_musica = carpetas[-2:] if len(carpetas) >= 2 else carpetas

            # 5. Creamos la lista final poniendo tu ruta elegida al principio
            ruta_final_partes = [nueva_ruta] + partes_musica

            # 6. os.path.join se encarga de unirlas usando las barras correctas (/ para Linux/macOS)
            nueva_linea = os.path.join(*ruta_final_partes)

            nuevo_archivo.write(nueva_linea + '\n')
            lineas_procesadas += 1

    return lineas_procesadas

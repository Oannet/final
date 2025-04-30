# sbac/core/versioning.py
import os
import json
import hashlib
from datetime import datetime
from rich import print
import difflib


SBAC_DIR = ".sbac"
INDEX_FILE = "index.json"
COMMITS_DIR = "commits"

def generar_hash_contenido(contenido: str) -> str:
    return hashlib.sha1(contenido.encode("utf-8")).hexdigest()

def leer_ultimo_commit():
    commits_path = os.path.join(SBAC_DIR, COMMITS_DIR)
    archivos = sorted([
        f for f in os.listdir(commits_path) if f.startswith("commit_") and f.endswith(".json")
    ])
    if not archivos:
        return None
    ruta_ultimo = os.path.join(commits_path, archivos[-1])
    with open(ruta_ultimo, "r", encoding="utf-8") as f:
        return json.load(f)

def commit(mensaje: str):
    if not mensaje.strip():
        print("[bold red]Error:[/bold red] El mensaje del commit no puede estar vacío.")
        return

    index_path = os.path.join(SBAC_DIR, INDEX_FILE)
    commits_path = os.path.join(SBAC_DIR, COMMITS_DIR)

    if not os.path.exists(index_path):
        print("[bold red]Error:[/bold red] No se encontró el repositorio o el índice. Usa 'sbac init' primero.")
        return

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception as e:
        print(f"[bold red]Error al leer el índice:[/bold red] {e}")
        return

    archivos = index_data.get("tracked_files", [])
    if not archivos:
        print("[bold yellow]No hay archivos en seguimiento para commitear.[/bold yellow]")
        return

    archivos_commit = []
    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"[bold red]Archivo no encontrado:[/bold red] {archivo}")
            continue

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
        except Exception as e:
            print(f"[bold red]Error al leer {archivo}:[/bold red] {e}")
            continue

        hash_archivo = generar_hash_contenido(contenido)

        archivos_commit.append({
            "path": archivo,
            "hash": hash_archivo,
            "content": contenido
        })

    if not archivos_commit:
        print("[bold yellow]Ningún archivo válido para guardar en el commit.[/bold yellow]")
        return

    # Validar si ya existe un commit con mismo estado de archivos
    ultimo = leer_ultimo_commit()
    if ultimo:
        archivos_anteriores = {f["path"]: f["hash"] for f in ultimo.get("files", [])}
        archivos_actuales = {f["path"]: f["hash"] for f in archivos_commit}

        if archivos_anteriores == archivos_actuales:
            print("[bold yellow]No hay cambios respecto al último commit. No se creó un nuevo commit.[/bold yellow]")
            return

    commit_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    commit_data = {
        "id": commit_id,
        "timestamp": datetime.now().isoformat(),
        "message": mensaje.strip(),
        "files": archivos_commit
    }

    ruta_commit = os.path.join(commits_path, f"commit_{commit_id}.json")
    try:
        with open(ruta_commit, "w", encoding="utf-8") as f:
            json.dump(commit_data, f, indent=4)
        print(f"[bold green]Commit creado correctamente:[/bold green] ID = {commit_id}")
    except Exception as e:
        print(f"[bold red]Error al guardar el commit:[/bold red] {e}")

def history():
    commits_path = os.path.join(SBAC_DIR, COMMITS_DIR)

    if not os.path.exists(commits_path):
        print("[bold red]Error:[/bold red] No existe la carpeta de commits.")
        return

    commits = sorted([
        f for f in os.listdir(commits_path) if f.startswith("commit_") and f.endswith(".json")
    ])

    if not commits:
        print("[bold yellow]No hay commits registrados todavía.[/bold yellow]")
        return

    print("[bold cyan]Historial de commits:[/bold cyan]")
    for filename in commits:
        path = os.path.join(commits_path, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"• [bold]{data['id']}[/bold] | {data['timestamp']} — [italic]{data['message']}[/italic]")
        except Exception as e:
            print(f"[bold red]Error al leer {filename}:[/bold red] {e}")

def crear_linea_base(nombre: str):
    if not nombre.strip():
        print("[bold red]Error:[/bold red] El nombre de la línea base no puede estar vacío.")
        return

    config_path = os.path.join(SBAC_DIR, "config.json")
    commits_path = os.path.join(SBAC_DIR, COMMITS_DIR)

    if not os.path.exists(config_path):
        print("[bold red]Error:[/bold red] No existe el repositorio. Ejecuta 'sbac init' primero.")
        return

    # Verifica si hay commits
    commits = sorted([
        f for f in os.listdir(commits_path)
        if f.startswith("commit_") and f.endswith(".json")
    ])

    if not commits:
        print("[bold yellow]No hay commits existentes para marcar como línea base.[/bold yellow]")
        return

    # Último commit
    ultimo_commit_archivo = commits[-1]
    ruta_ultimo = os.path.join(commits_path, ultimo_commit_archivo)

    try:
        with open(ruta_ultimo, "r", encoding="utf-8") as f:
            ultimo_commit = json.load(f)
    except Exception as e:
        print(f"[bold red]Error al leer último commit:[/bold red] {e}")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"[bold red]Error al leer config.json:[/bold red] {e}")
        return

    if "baselines" not in config:
        config["baselines"] = []

    # Validar duplicado
    if any(b["name"] == nombre for b in config["baselines"]):
        print(f"[bold yellow]Ya existe una línea base con el nombre '{nombre}'.[/bold yellow]")
        return

    nueva_base = {
        "name": nombre,
        "commit_id": ultimo_commit["id"],
        "timestamp": datetime.now().isoformat()
    }

    config["baselines"].append(nueva_base)

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print(f"[bold green]Línea base '{nombre}' creada correctamente.[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al guardar línea base:[/bold red] {e}")

def listar_lineas_base():
    config_path = os.path.join(SBAC_DIR, "config.json")

    if not os.path.exists(config_path):
        print("[bold red]Error:[/bold red] No existe el repositorio.")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"[bold red]Error al leer config.json:[/bold red] {e}")
        return

    baselines = config.get("baselines", [])
    if not baselines:
        print("[bold yellow]No hay líneas base registradas.[/bold yellow]")
        return

    print("[bold cyan]Líneas base registradas:[/bold cyan]")
    for base in baselines:
        print(f"• [bold]{base['name']}[/bold] → Commit {base['commit_id']} ({base['timestamp']})")

import difflib

def obtener_commit_por_id_o_baseline(ref: str):
    """Recibe una referencia (commit ID o nombre de línea base) y devuelve el commit."""
    commits_path = os.path.join(SBAC_DIR, COMMITS_DIR)
    config_path = os.path.join(SBAC_DIR, "config.json")

    # Si es un commit directo
    ruta_directa = os.path.join(commits_path, f"commit_{ref}.json")
    if os.path.exists(ruta_directa):
        with open(ruta_directa, "r", encoding="utf-8") as f:
            return json.load(f)

    # Si es un nombre de línea base
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            for base in config.get("baselines", []):
                if base["name"] == ref:
                    ruta_commit = os.path.join(commits_path, f"commit_{base['commit_id']}.json")
                    if os.path.exists(ruta_commit):
                        with open(ruta_commit, "r", encoding="utf-8") as f2:
                            return json.load(f2)
    print(f"[bold red]Error:[/bold red] No se encontró la referencia '{ref}' como commit ni línea base.")
    return None


def comparar_commits(v1: str, v2: str):
    c1 = obtener_commit_por_id_o_baseline(v1)
    c2 = obtener_commit_por_id_o_baseline(v2)

    if not c1 or not c2:
        return

    archivos1 = {f["path"]: f["content"] for f in c1.get("files", [])}
    archivos2 = {f["path"]: f["content"] for f in c2.get("files", [])}

    archivos_comunes = set(archivos1.keys()) & set(archivos2.keys())
    archivos_solo_1 = set(archivos1.keys()) - set(archivos2.keys())
    archivos_solo_2 = set(archivos2.keys()) - set(archivos1.keys())

    print(f"\n[bold cyan]Comparando versiones:[/bold cyan] {v1} ↔ {v2}\n")

    if archivos_comunes:
        for archivo in sorted(archivos_comunes):
            print(f"[bold yellow]Diferencias en: {archivo}[/bold yellow]")
            lineas1 = archivos1[archivo].splitlines()
            lineas2 = archivos2[archivo].splitlines()
            diff = list(difflib.unified_diff(lineas1, lineas2, fromfile=v1, tofile=v2, lineterm=""))
            if diff:
                for linea in diff:
                    print(linea)
            else:
                print("  (sin cambios)\n")
    else:
        print("[italic]No hay archivos comunes para comparar.[/italic]")

    if archivos_solo_1:
        print(f"\n[bold]Archivos solo en {v1}:[/bold] {', '.join(archivos_solo_1)}")
    if archivos_solo_2:
        print(f"[bold]Archivos solo en {v2}:[/bold] {', '.join(archivos_solo_2)}")

def restaurar_commit(ref: str):
    commit = obtener_commit_por_id_o_baseline(ref)

    if not commit:
        print(f"[bold red]No se encontró el commit o línea base '{ref}'[/bold red]")
        return

    archivos = commit.get("files", [])
    if not archivos:
        print("[bold yellow]No hay archivos en este commit para restaurar.[/bold yellow]")
        return

    print(f"[bold cyan]Restaurando archivos del commit {commit['id']}...[/bold cyan]")

    restaurados = []
    errores = []

    for archivo in archivos:
        ruta = archivo["path"]
        contenido = archivo["content"]

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            restaurados.append(ruta)
        except Exception as e:
            errores.append((ruta, str(e)))

    for archivo in restaurados:
        print(f"[green]✔ Restaurado:[/green] {archivo}")

    for ruta, error in errores:
        print(f"[red]✘ Error al restaurar {ruta}:[/red] {error}")

    if not errores:
        print(f"\n[bold green]¡Versión restaurada con éxito![/bold green]")
    else:
        print(f"\n[bold yellow]Se restauraron parcialmente los archivos. Revisa los errores arriba.[/bold yellow]")

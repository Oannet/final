import os
import json
from rich import print

def add_file(filename, repo_path=".sbac"):
    index_path = os.path.join(repo_path, "index.json")

    # Validar existencia
    if not os.path.exists(filename):
        print(f"[bold red]Error:[/bold red] El archivo '{filename}' no existe.")
        return

    # Validar que sea un archivo regular
    if not os.path.isfile(filename):
        print(f"[bold red]Error:[/bold red] '{filename}' no es un archivo regular.")
        return

    # Validar permisos de lectura
    if not os.access(filename, os.R_OK):
        print(f"[bold red]Error:[/bold red] No tienes permisos de lectura sobre '{filename}'.")
        return

    # Cargar el índice
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    except FileNotFoundError:
        print(f"[bold red]Error:[/bold red] No se encontró el archivo '{index_path}'. ¿Ejecutaste 'sbac init'?")
        return
    except json.JSONDecodeError:
        print(f"[bold red]Error:[/bold red] El archivo '{index_path}' está dañado o malformado.")
        return
    except Exception as e:
        print(f"[bold red]Error inesperado al leer el índice:[/bold red] {e}")
        return

    # Verificar duplicado
    tracked = index.get("tracked_files", [])
    if filename in tracked:
        print(f"[bold yellow]Advertencia:[/bold yellow] El archivo '{filename}' ya está siendo rastreado.")
        return

    # Agregar y guardar
    tracked.append(filename)
    index["tracked_files"] = tracked

    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=4)
        print(f"[bold green]Archivo '{filename}' añadido al seguimiento.[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al guardar el índice:[/bold red] {e}")
    
def show_status(repo_path=".sbac"):
    index_path = os.path.join(repo_path, "index.json")

    if not os.path.exists(index_path):
        print("[bold red]Error:[/bold red] No se encontró el índice de archivos.")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    tracked = index.get("tracked_files", [])
    
    if not tracked:
        print("[bold yellow]No hay archivos rastreados actualmente.[/bold yellow]")
        return

    print("[bold cyan]Archivos actualmente rastreados:[/bold cyan]")
    for file in tracked:
        print(f"  • {file}")


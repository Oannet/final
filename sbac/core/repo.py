# sbac/core/repo.py
import os
import json
from datetime import datetime
from rich import print

SBAC_DIR = ".sbac"
CONFIG_FILE = "config.json"
INDEX_FILE = "index.json"
COMMITS_DIR = "commits"
BASELINES_DIR = "baselines"

def init_repo():
    try:
        if os.path.exists(SBAC_DIR):
            if os.path.isdir(SBAC_DIR):
                print("[bold yellow]Advertencia:[/bold yellow] Ya existe un repositorio sbac en este directorio.")
                return
            else:
                print(f"[bold red]Error:[/bold red] Existe un archivo llamado '{SBAC_DIR}', no se puede crear el repositorio.")
                return

        # Crear estructura de carpetas
        os.makedirs(os.path.join(SBAC_DIR, COMMITS_DIR), exist_ok=True)
        os.makedirs(os.path.join(SBAC_DIR, BASELINES_DIR), exist_ok=True)

        # Configuración inicial
        config_data = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "commits": [],
            "baselines": []
        }
        with open(os.path.join(SBAC_DIR, CONFIG_FILE), "w", encoding="utf-8") as config_file:
            json.dump(config_data, config_file, indent=4)

        # Inicializar el índice de archivos seguidos
        index_data = {
            "tracked_files": []
        }
        with open(os.path.join(SBAC_DIR, INDEX_FILE), "w", encoding="utf-8") as index_file:
            json.dump(index_data, index_file, indent=4)

        print("[bold green]Repositorio sbac inicializado exitosamente.[/bold green]")

    except OSError as e:
        print(f"[bold red]Error de sistema:[/bold red] {e}")
    except Exception as e:
        print(f"[bold red]Error inesperado:[/bold red] {e}")

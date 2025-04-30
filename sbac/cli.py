import click
from sbac.core.repo import init_repo
from sbac.core.tracker import add_file 
from sbac.core import versioning


@click.group()
def cli():
    pass

@cli.command()
def init():
    """Inicializa un nuevo repositorio SBAC."""
    init_repo()

@cli.command()
@click.argument('archivo')
def add(archivo):
    """Añade un archivo al seguimiento."""
    add_file(archivo)

@cli.command()
def status():
    """Muestra el estado actual de archivos rastreados."""
    from sbac.core.tracker import show_status
    show_status()

@cli.command()
@click.argument("mensaje")
def commit(mensaje):
    """Crea un nuevo commit con un mensaje descriptivo."""
    versioning.commit(mensaje)

@cli.command()
def history():
    """Muestra el historial de commits guardados."""
    versioning.history()

@cli.command()
@click.argument("nombre")
def baseline(nombre):
    """Crea una línea base (baseline) con el nombre dado."""
    versioning.crear_linea_base(nombre)

@cli.command(name="list-baselines")
def list_baselines():
    """Lista todas las líneas base registradas."""
    versioning.listar_lineas_base()

@cli.command()
@click.argument("v1")
@click.argument("v2")
def diff(v1, v2):
    """Muestra diferencias entre dos versiones (commits o líneas base)."""
    versioning.comparar_commits(v1, v2)

@cli.command()
@click.argument("version")
def checkout(version):
    """Restaura los archivos desde un commit o línea base."""
    versioning.restaurar_commit(version)

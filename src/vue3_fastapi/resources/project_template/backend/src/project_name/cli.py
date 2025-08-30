import typer
from typing_extensions import Annotated
from rich import print
import importlib.metadata

app = typer.Typer(add_completion = False)

@app.command()
def version():
    print(f'[bold green]{{:新規作成するプロジェクト名:}} Version {importlib.metadata.version("{{:新規作成するプロジェクト名(小文字):}}")}[/bold green]')

@app.command()
def hello():
    print(f'[bold green]Hello, World![/bold green]')

if __name__ == "__main__":
    app()

import typer
from typing_extensions import Annotated
import inquirer
from pathlib import Path
import shutil
import subprocess
import re
from .new_project import NewProject
from rich import print
import importlib.metadata

options = {
    'typescript': 'TypeScript',
    'vue-router': 'Vue Router',
    'tailwindcss': 'TailwindCSS',
    'plotly': 'vue3-plotly',
    'scheduler': 'APScheduler',
    'cgi': 'ApacheのCGI用ファイル',
}

app = typer.Typer(add_completion = False)

def _validate_project_name(value: str) -> bool:
    return re.match(r'^[a-zA-Z0-9_-]+$', value) is not None

def _validate_parent_dir(value: Path) -> bool:
    return value.is_dir()

def _validate_python_version(value: str) -> bool:
    return re.match(r'^[0-9]+\.[0-9]+(\.[0-9]+)?$', value) is not None

def _validate_use_options(value: list[str]) -> bool:
    for option in value:
        if option not in options:
            return False
    return True

def _callback_project_name(value: str|None) -> str|None:
    if value and not _validate_project_name(value):
        raise typer.BadParameter('プロジェクト名はa-zA-Z0-9_-のみ使用できます。')
    return value

def _callback_parent_dir(value: Path|None) -> Path|None:
    if value and not _validate_parent_dir(value):
        raise typer.BadParameter('親フォルダーは存在するフォルダーを指定してください。')
    return value

def _callback_python_version(python_version: str|None) -> str|None:
    if python_version and not _validate_python_version(python_version):
        raise typer.BadParameter('Pythonバージョンは0.0.0形式で入力してください。')
    return python_version

def _callback_use_options(value: list[str]) -> list[str]:
    if not _validate_use_options(value):
        raise typer.BadParameter('次の機能が指定できます(複数指定可能): ' + ', '.join(options.keys()))
    return value

def _print_yes_no(value: bool) -> str:
    return 'はい' if value else 'いいえ'

def _check_command(command: str, version_check: bool=True) -> None:
    if shutil.which(command) is None:
        raise ValueError(f'{command}がインストールされていません。')
    if version_check:
        print(f'[green]{command}のバージョン:[/green] ', end='')
        result = subprocess.run([command, '--version'], check=True, capture_output=True)
        print(result.stdout.decode('utf-8').strip())
    else:
        print(f'[green]{command}[/green]: インストールされています。')

def _select_confirmation(message: str, default: bool) -> bool:
    result = inquirer.list_input(
        message=message,
        choices=[('はい', True), ('いいえ', False)],
        default=default,
    )
    return result

@app.command()
def new(
    project_name: Annotated[str|None, typer.Option('--name', '-n', help='新規作成するプロジェクト名', callback=_callback_project_name, show_envvar=False)] = None, 
    parent_dir: Annotated[Path|None, typer.Option('--dir', '-d', help='プロジェクトを保存する親フォルダー', callback=_callback_parent_dir, show_envvar=False)] =None, 
    python_version: Annotated[str|None, typer.Option('--python', '-p', help='Pythonバージョン', callback=_callback_python_version, show_envvar=False)] = None,
    use_options: Annotated[list[str], typer.Option('--use', '-u', help='使用する機能(複数指定可能): ' + ', '.join(options.keys()), callback=_callback_use_options, show_envvar=False)] = [],
):
    '''Vue3+FastAPIプロジェクトを新規作成します。'''

    print(f'[bold green]Vue3+FastAPI Project Generator Version {importlib.metadata.version("vue3-fastapi")}[/bold green]')
    try:
        print('[green]ツールを確認します。[/green]')
        _check_command('uv')
        _check_command('npm')
        _check_command('git')
        _check_command('wget', version_check=False)
        prompt = False

        if not project_name:
            prompt = True
            project_name = inquirer.text(
                message='新規作成するプロジェクト名を入力してください', 
                validate=lambda _, c: _validate_project_name(c),
            )
        if not parent_dir:
            prompt = True
            _dir = inquirer.path(
                message='プロジェクトを保存する親フォルダーを入力してください',
                default=str(Path.cwd()), 
                exists=True,
                path_type=inquirer.Path.DIRECTORY,
            )
            parent_dir = Path(_dir).resolve()
        else:
            parent_dir = parent_dir.resolve()
        assert (parent_dir is not None and project_name is not None)
        project_dir = parent_dir / project_name
        if project_dir.exists():
            raise ValueError(f'プロジェクトフォルダーはすでに存在します: {project_dir}')
        if not python_version:
            prompt = True
            python_version = inquirer.text(
                message='Pythonバージョンを入力してください',
                default='3.11',
                validate=lambda _, c: _validate_python_version(c),
            )
        if not use_options:
            prompt = True
            use_options = inquirer.checkbox(
                message='プロジェクトで使用する機能を選択してください',
                choices=[(label, value) for value, label in options.items()],
            )

    except Exception as e:
        print(f'[bold red]{e}[/bold red]')
        raise typer.Exit(1)

    print(f'''
> [green]新規作成するプロジェクト名:[/green] {project_name}
> [green]プロジェクトを保存する親フォルダー:[/green] {parent_dir}
> [green]Pythonバージョン:[/green] {python_version}''')
    for option in options.keys():
        print(f'> [green]{options[option]}:[/green] ', end='')
        if option in use_options:
            print('使用する')
        else:
            print('使用しない')
    print()
    if prompt:
        yes_or_no = _select_confirmation(
            message='上記の設定でプロジェクトを新規作成しますか?',
            default=True,
        )
        if not yes_or_no:
            raise typer.Exit(0)
    new_project = NewProject(
        project_name, 
        parent_dir, 
        python_version, 
        use_options, 
    )
    new_project.create()
    print('[bold green]プロジェクトの作成が完了しました:[/bold green] ', new_project.project_dir)

if __name__ == '__main__':
    app()

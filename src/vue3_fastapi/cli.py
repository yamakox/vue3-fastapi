import typer
import inquirer
from pathlib import Path
import shutil
import subprocess
import re
from .new_project import NewProject
from rich import print

app = typer.Typer()

def _validate_project_name(project_name: str) -> bool:
    return re.match(r'^[a-zA-Z0-9_-]+$', project_name) is not None

def _validate_parent_dir(parent_dir: str) -> bool:
    return Path(parent_dir).is_dir()

def _validate_python_version(python_version: str) -> bool:
    return re.match(r'^[0-9]+\.[0-9]+(\.[0-9]+)?$', python_version) is not None

def _callback_project_name(project_name: str|None) -> str|None:
    if project_name and not _validate_project_name(project_name):
        raise typer.BadParameter('プロジェクト名はa-zA-Z0-9_-のみ使用できます。')
    return project_name

def _callback_parent_dir(parent_dir: str|None) -> str|None:
    if parent_dir and not _validate_parent_dir(parent_dir):
        raise typer.BadParameter('親フォルダーは存在するフォルダーを指定してください。')
    return parent_dir

def _callback_python_version(python_version: str|None) -> str|None:
    if python_version and not _validate_python_version(python_version):
        raise typer.BadParameter('Pythonバージョンは0.0.0形式で入力してください。')
    return python_version

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

def _determine_switch_option(
        use_option: bool|None, 
        no_use_option: bool|None, 
        message: str, 
        default: bool,
) -> tuple[bool, bool]:
    if use_option is not None:
        return use_option, False
    if no_use_option is not None:
        return not no_use_option, False
    return _select_confirmation(message, default), True

@app.command()
def new(
    project_name: str|None=typer.Option(None, '--name', '-n', help='新規作成するプロジェクト名', callback=_callback_project_name), 
    parent_dir: str|None=typer.Option(None, '--dir', '-d', help='プロジェクトを保存する親フォルダー', callback=_callback_parent_dir), 
    python_version: str|None=typer.Option(None, '--python', '-p', help='Pythonバージョン', callback=_callback_python_version),
    use_typescript: bool|None=typer.Option(None, '--typescript', '-ts', help='TypeScriptを使用する'),
    use_vue_router: bool|None=typer.Option(None, '--vue-router', '-vr', help='Vue Routerを使用する'),
    use_tailwindcss: bool|None=typer.Option(None, '--tailwindcss', '-tw', help='TailwindCSSを使用する'),
    use_cgi: bool|None=typer.Option(None, '--cgi', '-c', help='ApacheのCGIとして使用する'),
    no_use_typescript: bool|None=typer.Option(None, '--no-typescript', '-nts', help='TypeScriptを使用しない'),
    no_use_vue_router: bool|None=typer.Option(None, '--no-vue-router', '-nvr', help='Vue Routerを使用しない'),
    no_use_tailwindcss: bool|None=typer.Option(None, '--no-tailwindcss', '-ntw', help='TailwindCSSを使用しない'),
    no_use_cgi: bool|None=typer.Option(None, '--no-cgi', '-nc', help='ApacheのCGIとして使用しない'),
):
    '''Vue3+FastAPIプロジェクトを新規作成します。'''
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
            parent_dir = inquirer.path(
                message='プロジェクトを保存する親フォルダーを入力してください',
                default=str(Path.cwd()), 
                exists=True,
                path_type=inquirer.Path.DIRECTORY,
            )
        if not python_version:
            prompt = True
            python_version = inquirer.text(
                message='Pythonバージョンを入力してください',
                default='3.11',
                validate=lambda _, c: _validate_python_version(c),
            )
        use_typescript, prompt = _determine_switch_option(
            use_typescript, no_use_typescript, 'TypeScriptを使用しますか?', True)
        use_vue_router, prompt = _determine_switch_option(
            use_vue_router, no_use_vue_router, 'Vue Routerを使用しますか?', True)
        use_tailwindcss, prompt = _determine_switch_option(
            use_tailwindcss, no_use_tailwindcss, 'TailwindCSSを使用しますか?', True)
        use_cgi, prompt = _determine_switch_option(
            use_cgi, no_use_cgi, 'ApacheのCGIとして使用しますか?', True)

        assert (parent_dir is not None and 
                project_name is not None and 
                python_version is not None and 
                use_typescript is not None and
                use_vue_router is not None and
                use_tailwindcss is not None and
                use_cgi is not None)
        project_dir = Path(parent_dir) / project_name
        if project_dir.exists():
            raise ValueError(f'プロジェクトフォルダーはすでに存在します: {project_dir}')
    except Exception as e:
        print(f'[bold red]{e}[/bold red]')
        raise typer.Exit(1)

    print(f'''
> [green]新規作成するプロジェクト名:[/green] {project_name}
> [green]プロジェクトを保存する親フォルダー:[/green] {parent_dir}
> [green]Pythonバージョン:[/green] {python_version}
> [green]TypeScriptの使用:[/green] {_print_yes_no(use_typescript)}
> [green]TailwindCSSの使用:[/green] {_print_yes_no(use_tailwindcss)}
> [green]Vue Routerの使用:[/green] {_print_yes_no(use_vue_router)}
> [green]ApacheのCGIとして使用:[/green] {_print_yes_no(use_cgi)}
''')
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
        use_typescript, 
        use_tailwindcss, 
        use_vue_router, 
        use_cgi, 
    )
    new_project.create()
    print('[bold green]プロジェクトの作成が完了しました:[/bold green] ', new_project.project_dir)

if __name__ == '__main__':
    app()

import typer
from rich import print
from pathlib import Path
import subprocess
import shutil
from . import resource_path
from . import util
import re
import json
import os

project_template_path = resource_path / 'project_template'
scheduler_path = resource_path / 'apscheduler'
fastapi_cgi_path = resource_path / 'fastapi_cgi'
plotly_path = resource_path / 'plotly'
vue_router_path = resource_path / 'vue-router'

class NewProject:
    def __init__(
            self, 
            project_name: str, 
            parent_dir: Path, 
            python_version: str, 
            use_options: list[str], 
    ):
        self.project_name = project_name
        self.parent_dir = parent_dir
        self.python_version = python_version
        self.use_options = use_options
        self.__init_option_variables()
        self.project_dir = self.parent_dir / self.project_name
        self.package_name = project_name.replace('-', '_').lower()
        self.__init_variables()

    def __init_option_variables(self):
        self.use_typescript = 'typescript' in self.use_options
        self.use_vue_router = 'vue-router' in self.use_options
        self.use_tailwindcss = 'tailwindcss' in self.use_options
        self.use_plotly = 'plotly' in self.use_options
        self.use_scheduler = 'scheduler' in self.use_options
        self.use_cgi = 'cgi' in self.use_options

    def create(self):
        # avoid warning: `VIRTUAL_ENV=/.../.venv` does not match the project environment path `.venv` and will be ignored
        if 'VIRTUAL_ENV' in os.environ:
            del os.environ['VIRTUAL_ENV']
        try:
            self.__create_project_dir()
            self.__create_backend()
            self.__create_frontend()
            self.__copy_project_root_files()
            self.__wget_gitignore()
            self.__setup_backend()
            self.__setup_frontend()
            if self.use_tailwindcss:
                self.__setup_tailwindcss()
            if self.use_vue_router:
                self.__copy_vue_router_files()
            if self.use_plotly:
                self.__copy_plotly_files()
            self.__copy_vscode_files()
            if self.use_scheduler:
                self.__copy_scheduler_files()
            if self.use_cgi:
                self.__copy_fastapi_cgi_files()
                self.__modify_fastapi_cgi_tasks_json()
            self.__init_git()
            self.__finalize_backend()
        except Exception as e:
            print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(1)

    def __init_variables(self):
        self.variables = {
            '新規作成するプロジェクト名': self.project_name, 
            '新規作成するプロジェクト名(小文字)': self.project_name.lower(), 
            'Pythonバージョン': self.python_version, 
            'Pythonパッケージ名': self.package_name, 
            'additional_imports': '', 
            'lifespan_init': '', 
            'lifespan_exit': '', 
        }

        additional_imports = ''
        lifespan_init = ''
        lifespan_exit = ''

        if self.use_scheduler:
            additional_imports += 'from . import scheduler\n'
            lifespan_init += '    scheduler.start()\n'
            lifespan_exit += '    scheduler.stop()\n'

        self.variables['additional_imports'] = additional_imports
        self.variables['lifespan_init'] = lifespan_init if lifespan_init else '    pass\n'
        self.variables['lifespan_exit'] = lifespan_exit if lifespan_exit else '    pass\n'

    def __create_project_dir(self):
        print(f'[green]新規プロジェクトのフォルダーを作成します:[/green] {self.project_dir}')
        self.project_dir.mkdir(parents=True, exist_ok=True)

    def __create_backend(self):
        self.backend_dir = self.project_dir / 'backend'
        print(f'[green]backend用プロジェクト(Python+FastAPI)を作成します:[/green] {self.backend_dir}')
        subprocess.run(
            ['uv', 'init', '--python', self.python_version, '--build-backend', 'poetry', '--vcs', 'none', self.project_name], 
            cwd=self.project_dir, 
            check=True,
        )
        (self.project_dir / self.project_name).rename(self.backend_dir)

    def __create_frontend(self):
        self.frontend_dir = self.project_dir / 'frontend'
        print(f'[green]frontend用プロジェクト(Vue3)を作成します:[/green] {self.frontend_dir}')
        frontend_name = self.project_name.lower()
        template = 'vue-ts' if self.use_typescript else 'vue'
        subprocess.run(
            ['npm', 'create', 'vite@latest', frontend_name, '--', '--template', template, '--no-interactive', '--no-rolldown'], 
            cwd=self.project_dir, 
            check=True,
        )
        (self.project_dir / frontend_name).rename(self.frontend_dir)

    def __copy_project_root_files(self):
        print('[green]新規プロジェクトのルートファイルをコピーします。[/green]')
        for file in project_template_path.glob('*'):
            if file.is_file():
                util.copy_file_with_variables(file, self.project_dir / file.name, self.variables)

    def __wget_gitignore(self):
        print('[green].gitignoreをダウンロードします。[/green]')
        python_gitignore = self.project_dir / 'backend/.gitignore'
        subprocess.run(
            ['wget', '-O', python_gitignore, 'https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore'], 
            cwd=self.project_dir, 
            check=True,
        )
        util.replace_text_of_file(python_gitignore, {
            r'\.env\..*': '',
        })
        node_gitignore = self.project_dir / 'frontend/.gitignore'
        subprocess.run(
            ['wget', '-O', node_gitignore, 'https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore'], 
            cwd=self.project_dir, 
            check=True,
        )
        util.replace_text_of_file(node_gitignore, {
            r'^\.env\..*': '',
        })

    def __setup_backend(self):
        print('[green]backendの設定を行います。[/green]')
        backend_dir = self.project_dir / 'backend'
        subprocess.run(
            ['uv', 'add', 'fastapi', 'uvicorn', 'python-dotenv', 'typer'], 
            cwd=backend_dir, 
            check=True,
        )
        subprocess.run(
            ['uv', 'add', '--dev', 'debugpy'], 
            cwd=backend_dir, 
            check=True,
        )
        if self.use_scheduler:
            subprocess.run(
                ['uv', 'add', 'apscheduler', 'python-dateutil'], 
                cwd=backend_dir, 
                check=True,
            )
        if self.use_cgi:
            subprocess.run(
                ['uv', 'add', 'a2wsgi'], 
                cwd=backend_dir, 
                check=True,
            )
        self.__copy_backend_files()
        self.__add_lines_to_backend_gitignore()
        self.__modify_backend_pyproject_toml()
        print('[green]backendの設定を完了しました。[/green]')

    def __copy_backend_files(self):
        print('[green]backendのファイルをコピーします。[/green]')
        src_dir = project_template_path / 'backend/src/project_name'
        dst_dir = self.project_dir / 'backend/src' / self.package_name
        util.copy_dir_with_variables(src_dir, dst_dir, self.variables)

    def __add_lines_to_backend_gitignore(self):
        print('[green]backend/.gitignoreに必要な行を追加します。[/green]')
        gitignore = self.project_dir / 'backend/.gitignore'
        with open(gitignore, 'a') as f:
            f.write('\npublic/\n')

    def __modify_backend_pyproject_toml(self):
        print('[green]backend/pyproject.tomlを修正します。[/green]')
        pyproject_toml = self.project_dir / 'backend/pyproject.toml'
        util.replace_text_of_file(pyproject_toml, {
            r'^version = .*': 'dynamic = ["version"]',
            r'^requires = \["poetry-core.*': 'requires = ["poetry-core>=2.0.0,<3.0.0", "poetry-dynamic-versioning>=1.0.0,<2.0.0"]', 
            r'^build-backend = .*': 'build-backend = "poetry_dynamic_versioning.backend"',
            r'^(\[project.scripts\]\n)': f'\\1{self.project_name.lower()}-cli = "{self.package_name}.cli:app"\n',
        })
        with open(pyproject_toml, 'a') as f:
            f.write(f'''
[tool.poetry]
packages = [{{include = "{self.package_name}", from = "src"}}]
include = [{{path = "src/{self.package_name}/public/**/*", format = ["sdist", "wheel"]}}]
version = "0.0.0"

[tool.poetry.requires-plugins]
poetry-dynamic-versioning = {{version = ">=1.0.0,<2.0.0", extras = ["plugin"]}}

[tool.poetry-dynamic-versioning]
enable = true
pattern = '(?P<base>\\d+\\.\\d+\\.\\d+)'
''')

    def __finalize_backend(self):
        print('[green]backendの設定を完了します。[/green]')
        backend_dir = self.project_dir / 'backend'
        subprocess.run(
            ['uv', 'sync', '--no-dev'], 
            cwd=backend_dir, 
            check=True,
        )

    def __setup_frontend(self):
        print('[green]frontendの設定を行います。[/green]')
        frontend_dir = self.project_dir / 'frontend'
        subprocess.run(
            ['npm', 'install', '--save-dev', 
             'prettier', 'prettier-plugin-tailwindcss', 
             'eslint', 'eslint-plugin-vue', 
             'vite-plugin-vue-devtools', 
             '@types/node', ], 
            cwd=frontend_dir, 
            check=True,
        )
        self.__copy_frontend_files()
        self.__add_lines_to_frontend_gitignore()
        self.__modify_frontend_index_html()
        if self.use_typescript:
            self.__modify_frontend_tsconfig_app_json()
        print('[green]frontendの設定を完了しました。[/green]')

    def __copy_frontend_files(self):
        print('[green]frontendのファイルをコピーします。[/green]')
        src_dir = project_template_path / 'frontend'
        dst_dir = self.project_dir / 'frontend'
        for i in src_dir.glob('*'):
            if i.is_file():
                util.copy_file_with_variables(i, dst_dir / i.name, self.variables)
        src_dir = project_template_path / ('frontend/ts' if self.use_typescript else 'frontend/js')
        dst_dir = self.project_dir / 'frontend'
        util.copy_dir_with_variables(src_dir, dst_dir, self.variables)

    def __add_lines_to_frontend_gitignore(self):
        print('[green]frontend/.gitignoreに必要な行を追加します。[/green]')
        gitignore = self.project_dir / 'frontend/.gitignore'
        with open(gitignore, 'a') as f:
            f.write('\n*.tar.xz\n')

    def __modify_frontend_index_html(self):
        print('[green]frontend/index.htmlを修正します。[/green]')
        index_html = self.project_dir / 'frontend/index.html'
        util.replace_text_of_file(index_html, {
            r'<title>[^<]*</title>': f'<title>{self.project_name}</title>',
        })

    def __modify_frontend_tsconfig_app_json(self):
        print('[green]frontend/tsconfig.app.jsonを修正します。[/green]')
        tsconfig_app_json = self.project_dir / 'frontend/tsconfig.app.json'
        with open(tsconfig_app_json, 'r') as f:
            lines = f.readlines()
        i = 0
        while i < len(lines):
            if re.search(r'"compilerOptions":', lines[i]):
                i += 1
                lines.insert(i, '    "target": "ES2023",\n')
                lines.insert(i + 1, '    "lib": ["ES2023", "DOM"],\n')
                lines.insert(i + 2, '    "module": "ESNext",\n')
                i += 3
                break
            i += 1
        lines.insert(-1, '  , "paths": {"@/*": ["./src/*"]}\n')
        with open(tsconfig_app_json, 'w') as f:
            f.writelines(lines)

    def __setup_tailwindcss(self):
        print('[green]TailwindCSSの設定を行います。[/green]')
        frontend_dir = self.project_dir / 'frontend'
        subprocess.run(
            ['npm', 'install', '--save-dev', 
                'tailwindcss', '@tailwindcss/vite', ], 
            cwd=frontend_dir, 
            check=True,
        )
        vite_config_path = self.project_dir / 'frontend/vite.config.js'
        if not vite_config_path.exists():
            vite_config_path = self.project_dir / 'frontend/vite.config.ts'
        util.replace_text_of_file(vite_config_path, {
            r'(import vue from "@vitejs/plugin-vue")(;)?\n': r'\1\2\nimport tailwindcss from "@tailwindcss/vite"\2\n',
            r'plugins: \[([^\]]+)\],': r'plugins: [\1, tailwindcss()],',
        })

    def __copy_vue_router_files(self):
        print('[green]Vue Routerの設定を行います。[/green]')
        frontend_dir = self.project_dir / 'frontend'
        subprocess.run(
            ['npm', 'install', '--save-dev', 'vue-router', ], 
            cwd=frontend_dir, 
            check=True,
        )
        app_src_path = self.frontend_dir / 'src/App.vue'
        app_dst_path = self.frontend_dir / 'src/pages/Home.vue'
        util.copy_file_with_variables(app_src_path, app_dst_path, self.variables)
        util.replace_text_of_file(app_dst_path, {
            r'\./components/': '../components/',
            r'\./assets/': '../assets/',
        })
        if self.use_typescript:
            src_dir = vue_router_path / 'ts/src'
            main_path = self.project_dir / 'frontend/src/main.ts'
        else:
            src_dir = vue_router_path / 'js/src'
            main_path = self.project_dir / 'frontend/src/main.js'
        dst_dir = self.project_dir / 'frontend/src'
        util.copy_dir_with_variables(src_dir, dst_dir, self.variables)
        util.replace_text_of_file(main_path, {
            r"(import App from './App.vue')(;)?\n": r"\1\2\nimport router from './router';",
            r"(createApp\(App\))": r"\1.use(router)",
        })

    def __copy_plotly_files(self):
        print('[green]vue3-plotlyの設定を行います。[/green]')
        frontend_dir = self.project_dir / 'frontend'
        subprocess.run(
            ['npm', 'install', '--save', '@yamakox/vue3-plotly', 'plotly.js-dist-min', ], 
            cwd=frontend_dir, 
            check=True,
        )
        if self.use_typescript:
            subprocess.run(
                ['npm', 'install', '--save-dev', '@types/plotly.js', 'vue-component-type-helpers', ], 
                cwd=frontend_dir, 
                check=True,
            )
            src_dir = plotly_path / 'ts/src'
        else:
            src_dir = plotly_path / 'js/src'
        dst_dir = self.project_dir / 'frontend/src'
        util.copy_dir_with_variables(src_dir, dst_dir, self.variables)

    def __copy_vscode_files(self):
        print('[green].vscodeフォルダーをコピーします。[/green]')
        src_dir = project_template_path / '.vscode'
        dst_dir = self.project_dir / '.vscode'
        util.copy_dir_with_variables(src_dir, dst_dir, self.variables)

    def __copy_scheduler_files(self):
        print('[green]APSchedulerの設定を行います。[/green]')
        src_dir = scheduler_path / 'src/project_name'
        dst_dir = self.project_dir / 'backend/src' / self.package_name
        util.copy_dir_with_variables(src_dir, dst_dir, self.variables)

    def __copy_fastapi_cgi_files(self):
        print('[green]CGI用ファイルをコピーします。[/green]')
        src_dir = fastapi_cgi_path / 'cgi'
        dst_dir = self.project_dir / 'cgi'
        util.copy_dir_with_variables(src_dir, dst_dir, self.variables)
        util.copy_file_with_variables(
            fastapi_cgi_path / '.env.cgi', 
            self.project_dir / 'frontend/.env.cgi', 
            self.variables
        )

    def __modify_fastapi_cgi_tasks_json(self):
        print('[green]tasks.jsonを修正します。[/green]')
        src_tasks_json_path = fastapi_cgi_path / 'tasks.json'
        dst_tasks_json_path = self.project_dir / '.vscode/tasks.json'
        with open(src_tasks_json_path, 'r') as f:
            src_tasks_json = json.load(f)
        with open(dst_tasks_json_path, 'r') as f:
            dst_tasks_json = json.load(f)
        dst_tasks_json['tasks'].extend(src_tasks_json['tasks'])
        with open(dst_tasks_json_path, 'w') as f:
            json.dump(dst_tasks_json, f, indent=2)

    def __init_git(self):
        print('[green]gitリポジトリを初期化します。[/green]')
        subprocess.run(
            ['git', 'init'], 
            cwd=self.project_dir, 
            check=True,
        )
        subprocess.run(
            ['git', 'branch', '-M', 'main'], 
            cwd=self.project_dir, 
            check=True,
        )
        subprocess.run(
            ['git', 'add', '.'], 
            cwd=self.project_dir, 
            check=True,
        )
        subprocess.run(
            ['git', 'commit', '-m', 'Initial commit'], 
            cwd=self.project_dir, 
            check=True,
        )
        subprocess.run(
            ['git', 'tag', 'v0.0.0'], 
            cwd=self.project_dir, 
            check=True,
        )

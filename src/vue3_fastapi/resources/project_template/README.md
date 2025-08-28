# {{:新規作成するプロジェクト名:}} アプリケーション (Vue3 + FastAPI)

本アプリケーションは[vue3-fastapi-prompt](https://github.com/yamakox/vue3-fastapi-prompt)を使ってプロジェクトを生成しています。

## ファイル一覧

### frontendフォルダー

TypeScriptを選択すると、`npm create vite@latest -- --template vue-ts`コマンドでVue+TypeScriptのプロジェクトを生成した後、viteやtsconfigの設定をカスタマイズしています。以下はVue Routerを使った場合のファイル構成です。

```bash -c "tree -I '.venv|node_modules|__pycache__' frontend"
frontend
├── README.md
├── index.html
├── package-lock.json
├── package.json                # npm installコマンドでパッケージ追加してください
├── public                      # 静的ファイルはここに格納してください
│   └── vite.svg
├── src
│   ├── App.vue                 # Vue Routerを使うと、デフォルトのApp.vueはHome.vueに移動します
│   ├── assets                  # Vueコンポーネントで使う静的ファイルはここに格納してください
│   │   └── vue.svg
│   ├── components
│   │   ├── HelloFastAPI.vue    # backendのexampleモジュールで実装したAPIのサンプルコンポーネントです
│   │   └── HelloWorld.vue
│   ├── main.ts
│   ├── pages                   # Vue Routerを使うと、pagesフォルダーの中でページ用コンポーネントを格納します
│   │   └── Home.vue
│   ├── router
│   │   └── index.ts            # Vue Routerのルーティング設定です
│   ├── style.css
│   └── vite-env.d.ts
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

Vueアプリケーションの作成手順は以下を想定しています。

- 再利用可能なコンポーネントは`components`フォルダーに格納する
- Vue Routerを使う場合:
  - `pages`フォルダーにページコンポーネントを追加する
  - `router/index.ts`にページコンポーネントのルーティング設定を追加する
- Vue Routerを使わない場合:
  - `App.vue`にアプリの機能を実装する

`App.vue`(Vue Routerを使用しない場合)または`Home.vue`(Vue Routerを使用する場合)をテキストエディタで開き、`HelloWorld.vue`を`HellowFastAPI.vue`に置き換えると、FastAPIの動作確認ができます。

### backendフォルダー

`uv init`コマンドでPythonのプロジェクトを生成した後、FastAPIのサンプルコードを追加しています。

```bash -c "tree -I '.venv|node_modules|__pycache__' backend"
backend
├── README.md
├── pyproject.toml              # uv addコマンドでパッケージ追加してください
├── src
│   └── {{:Pythonパッケージ名:}}
│       ├── __init__.py         # FastAPIアプリケーションインスタンスを生成します(create_app関数)
│       ├── __main__.py         # FastAPIアプリケーションを起動します (python -m {{:Pythonパッケージ名:}})
│       ├── api
│       │   ├── __init__.py       # APIモジュール (/api/)
│       │   └── v1                # APIをバージョンごとに格納します
│       │       ├── __init__.py   # APIモジュール (/api/v1/)
│       │       └── example.py    # example APIモジュール (/api/v1/example)
│       ├── common              # 共通モジュール
│       │   ├── logger.py       # ロガーモジュール
│       │   └── settings.py     # 設定モジュール(環境変数の値を取得する)
│       ├── frontend.py         # publicフォルダーをWeb公開するモジュール(Vue Routerに対応)
│       └── public              # frontendフォルダーで`npm run build`すると生成されます
└── uv.lock
```

FastAPIアプリケーションの作成手順は以下を想定しています。

- RESTful APIは`api`フォルダーの中にAPIモジュールを追加する
  - `v1`, `v2`などのバージョンごとにサブフォルダーを作ることを想定している
- DBなどの設定値は`.env`ファイルを使って環境変数で渡す
  - `.env`の設定項目は`common/settings.py`で一元管理する
- `npm run build -- --mode backend`で生成したVueアプリケーションは`public`フォルダーに格納される
  - `frontend.py`がFastAPIのアプリケーションインスタンスを通じて`public`フォルダーの内容をWeb公開しており、静的ファイルの公開方法をカスタマイズするときは`frontend.py`の処理を変更する

FastAPIアプリケーションはuvによって`backend/.venv`が作成されています。CursorやvscodeでPythonインタープリターを選択するときは`backend/.venv/bin/python`を指定してください。

## .vscode設定

### デバッガの設定

- **debug frontend (requires vite dev server running)**: `npm run dev`でVite開発サーバが起動している場合、Google Chromeを使ってVueアプリケーションをデバッグできます。
- **debug server (fastapi)**: FastAPIアプリケーションのデバッグを開始します。

### タスクの設定

- **start vite dev server**: `npm run dev`を実行してVite開発サーバを起動します。
- **npm run build (for production)**: `npm run build`を実行してVueアプリケーションをビルドします。ビルドに成功すると`frontend/dist`フォルダーにビルドしたVueアプリケーションが格納されます。
- **build FastAPI server**: 以下のビルド処理が実行されます。
  - `npm run build -- --mode backend`を実行してVueアプリケーションをビルドします。ビルドに成功すると`backend/public`フォルダーにビルドしたVueアプリケーションが格納されます。
  - `uv build`を実行してFastAPIアプリケーションをビルドします。`backend/public`フォルダーに格納されたVueアプリケーションもPythonパッケージに格納されます。
- **build FastAPI via CGI**: ApacheのCGIとして使用する場合のビルド処理が実行されます。
  - Apacheでは`/{{:新規作成するプロジェクト名:}}/index.cgi`となるように`cgi`フォルダー内の`index.cgi`と`.htaccess`をApacheのWeb公開フォルダーに格納します。
  - `index.cgi`の1行目(shebang)にPythonのパス名を設定してください。初期値の`#!/home/ユーザー名/.venv/bin/python`ままでは動作しません。
  - `index.cgi`に設定したPythonを使って、ビルドしたwheelファイル(`.whl`)をインストールしてください。(`python -m pip install`)

## Dockerfile

プロジェクトのフォルダー直下にあるDockerfileでコンテナイメージをビルド・実行できます。

```bash
docker build -t {{:新規作成するプロジェクト名(小文字):}}:latest .
docker run -it --rm -p 8000:8000 {{:新規作成するプロジェクト名(小文字):}}
```

起動したら、`http://localhost:8000/`にアクセスしてください。

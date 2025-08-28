#!/home/ユーザー名/.venv/bin/python

from wsgiref.handlers import CGIHandler
from {{:Pythonパッケージ名:}} import create_app
from a2wsgi import ASGIMiddleware

# .htaccessでパスを書き換えて、FastAPIには`/{{:新規作成するプロジェクト名:}}/index.cgi/パス`が渡される
app = create_app(base_url='/{{:新規作成するプロジェクト名:}}/index.cgi')
app = ASGIMiddleware(app)

CGIHandler().run(app)

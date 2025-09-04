from pathlib import Path
import os

# MARK: environment variables

NAME = os.environ.get('NAME', '{{:新規作成するプロジェクト名:}}')
PORT = int(os.environ.get('PORT', 8000))
APP_DEBUG = int(os.environ.get('APP_DEBUG', "0"))
BASE_URL = os.environ.get('BASE_URL', '/')
FRONTEND_URLS = os.environ.get('FRONTEND_URLS', 'http://localhost:5173')   # カンマ区切りで複数のURLを指定可能

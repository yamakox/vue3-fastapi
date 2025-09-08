from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager
from . import api
from . import frontend
from .common.logger import logger
from .common import settings
{{:additional_imports:}}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ToDo: 初期化処理
{{:lifespan_init:}}
    yield   # app実行中にここに到達する

    # ToDo: 終了処理
{{:lifespan_exit:}}
# MARK: create an app
def create_app(base_url: str = '') -> FastAPI:
    base_path = Path(__file__).parent.resolve()
    logger.debug(f'create_app {base_url=} {base_path=}')

    # Create an application instance
    app = FastAPI(lifespan=lifespan, root_path=base_url)

    # CORS対策
    if settings.FRONTEND_URLS:
        origins = [i.strip().removesuffix('/') for i in settings.FRONTEND_URLS.split(',') if i.strip()]
    else:
        origins = ['http://localhost:5173']

    app.add_middleware(
        CORSMiddleware, 
        allow_origins=origins, 
        allow_credentials=True, 
        allow_methods=['*'], 
        allow_headers=['*'], 
    )

    # Initialize application instance
    app.include_router(api.v1.create_router(base_path=base_path))
    app.include_router(frontend.create_router(base_path=base_path))

    logger.debug(f'create_app {app.routes=} {app.root_path=}')

    return app

# MARK: main
def main():
    import uvicorn
    app = create_app(
        base_url=settings.BASE_URL.removesuffix('/')
    )
    uvicorn.run(app, host='0.0.0.0', port=settings.PORT)

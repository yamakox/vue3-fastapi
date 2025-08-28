import importlib
import pkgutil
from fastapi import APIRouter
from pathlib import Path

def create_router(base_path: Path) -> APIRouter:
    # MARK: /api/v1
    router = APIRouter(prefix="/api/v1", tags=['API v1'])
    
    # モジュールを探索し、routerを取得してマウント
    package_name = __name__
    package_path = Path(__file__).parent.resolve()
    for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
        module = importlib.import_module(f"{package_name}.{module_name}")
        if hasattr(module, "create_router"):
            router.include_router(module.create_router(base_path=base_path))
    
    return router

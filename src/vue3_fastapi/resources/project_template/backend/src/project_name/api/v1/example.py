from fastapi import APIRouter
from pathlib import Path
import threading

# global variables
lock = threading.Lock()
counter = 0

def create_router(base_path: Path) -> APIRouter:
    # MARK: /api/v1/example
    router = APIRouter(prefix="/example", tags=['example'])
    
    # MARK: /api/v1/example/hello
    @router.get("/hello")
    def get_hello():
        return {"message": "Hello, FastAPI!"}
    
    # MARK: /api/v1/example/counter
    @router.get("/counter")
    def get_counter():
        return {"counter": counter}
    
    # MARK: /api/v1/example/count_up
    @router.get("/count_up")
    def count_up():
        with lock:
            global counter
            counter += 1
            return {"counter": counter}

    return router

import uvicorn as uvicorn
from dotenv import load_dotenv

load_dotenv()

def run_api(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    workers: int = 1
):
    """Запуск FastAPI приложения через Uvicorn"""
    uvicorn.run(
        "API.app:app",
        host=host,
        port=port,
        reload=reload, 
        workers=workers,
    )


if __name__ == "__main__":
    """Поехали!"""
    run_api(
        host="127.0.0.1",
        port=8000,
        reload=True
    )

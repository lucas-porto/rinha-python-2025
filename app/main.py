import asyncio
import uvicorn
from starlette.applications import Starlette

# Importar rotas
from .routes.healthcheck import router as health_router
from .routes.payments import router as payments_router
from .routes.purge import router as purge_router


# Combinar todas as rotas
all_routes = [
    *health_router,
    *payments_router,
    *purge_router,
]

app = Starlette(routes=all_routes)


async def main():
    print("Starting server...")

    from .database import database

    try:
        await database.initialize()
    except Exception as e:
        print(f"Storage não inicializado: {e}")

    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=9999,
        reload=False,
        loop="uvloop",
        http="httptools",
        workers=1,
        log_level="info",
    )
    server = uvicorn.Server(config)
    print("Server configured, starting...")
    await server.serve()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

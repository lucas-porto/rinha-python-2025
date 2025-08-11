from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.database.redis_pool import redis_client


async def purge_payments() -> JSONResponse:
    try:
        await redis_client.delete("default", "fallback")

        return JSONResponse(status_code=200, content="Database purged")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error purging databased: {e}")


router = [
    Route("/purge", purge_payments, methods=["POST"]),
]

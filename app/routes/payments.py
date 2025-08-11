import asyncio
import orjson
from datetime import datetime, timezone
from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import JSONResponse, Response
from starlette.exceptions import HTTPException
from app.database.redis_pool import redis_client
from app.database.storage import KEY_SET
from app.utils import (
    iso_to_timestamp,
    get_redis_range,
    REDIS_TIMEOUT,
    calculate_summary,
)


async def create_payment(request: Request) -> Response:
    try:
        body = await request.body()

        if not body:
            raise HTTPException(status_code=400, detail="Bad request")

        payment_data = orjson.loads(body)

        # Adicionar timestamp original da requisição
        current_time = datetime.now(timezone.utc)
        payment_data["requested_at"] = current_time.isoformat()

        # Colocar na fila Redis com timestamp preservado
        await redis_client.rpush("payment_queue", orjson.dumps(payment_data))

        return Response(status_code=201)
    except Exception as e:
        if "OOM" in str(e) or "memory" in str(e).lower():
            return Response(status_code=503)
        return Response(status_code=500, content=str(e))


async def get_payment(request: Request) -> JSONResponse:
    try:
        from_request = request.query_params.get("from")
        to_request = request.query_params.get("to")

        min_score = "-inf"
        max_score = "+inf"

        if from_request:
            timestamp, success = iso_to_timestamp(from_request)
            if success and timestamp is not None:
                min_score = timestamp

        if to_request:
            timestamp, success = iso_to_timestamp(to_request)
            if success and timestamp is not None:
                max_score = timestamp

        # Buscar todos os pagamentos na chave KEY_SET
        all_payments_task = asyncio.create_task(
            get_redis_range(KEY_SET, min_score, max_score)
        )

        try:
            all_payments = await asyncio.wait_for(
                all_payments_task, timeout=REDIS_TIMEOUT
            )
        except asyncio.TimeoutError:
            all_payments = []

    except Exception:
        all_payments = []

    default_items = []
    fallback_items = []

    for payment in all_payments:
        try:
            payment_data = orjson.loads(payment)
            processor = payment_data.get("processor", "default")
            if processor == "default":
                default_items.append(payment)
            elif processor == "fallback":
                fallback_items.append(payment)
        except (ValueError, TypeError, orjson.JSONDecodeError):
            continue

    default_summary = await calculate_summary(default_items, "default")
    fallback_summary = await calculate_summary(fallback_items, "fallback")

    return JSONResponse(
        status_code=200,
        content={
            "default": default_summary,
            "fallback": fallback_summary,
        },
    )


router = [
    Route("/payments", create_payment, methods=["POST"]),
    Route("/payments-summary", get_payment, methods=["GET"]),
]

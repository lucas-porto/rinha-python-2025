import asyncio
import orjson
from app.database.storage import save_payment
from app.database.redis_pool import redis_client
from app.processor.processor import process_payment_in_processor
from datetime import datetime


BATCH_SIZE = 1
MAX_CONCURRENT_REQUESTS = 10
NUM_WORKERS = 3
MAX_RETRIES = 3
IDLE_SLEEP = 0.01
ERROR_SLEEP = 0.1


async def process_payment_with_fallback(
    payment_data: dict, retry_count: int = 0
) -> bool:
    requested_at = datetime.fromisoformat(
        payment_data["requested_at"].replace("Z", "+00:00")
    ).replace(tzinfo=None)  # Remover timezone para usar UTC

    # Tentar primeiro o processor default
    try:
        result = await process_payment_in_processor(
            payload=payment_data, processor_type="default"
        )

        # Se o default processou com sucesso, salvar
        if result != "not avaiable":
            await save_payment(
                cid=payment_data["correlationId"],
                amount=payment_data["amount"],
                processor="default",
                requested_at=requested_at,
            )
            return True

    except Exception:
        pass

    # Se o default falhou ou não está disponível, tentar fallback
    try:
        result = await process_payment_in_processor(
            payload=payment_data, processor_type="fallback"
        )

        # Se o fallback processou com sucesso, salvar
        if result != "not avaiable":
            await save_payment(
                cid=payment_data["correlationId"],
                amount=payment_data["amount"],
                processor="fallback",
                requested_at=requested_at,
            )
            return True

    except Exception:
        pass

    # Se ambos falharam, salvar como erro
    await save_payment(
        cid=payment_data["correlationId"],
        amount=payment_data["amount"],
        processor="error",
        requested_at=requested_at,
    )
    return True


async def process_payment_queue(semaphore: asyncio.Semaphore):
    while True:
        try:
            async with semaphore:
                payment_data = await redis_client.lpop("payment_queue")

                if payment_data:
                    if isinstance(payment_data, bytes):
                        payment_data = orjson.loads(payment_data)

                    if isinstance(payment_data, str):
                        payment_data = orjson.loads(payment_data)

                    if "retry_count" not in payment_data:
                        payment_data["retry_count"] = 0

                    await process_payment_with_fallback(
                        payment_data, payment_data["retry_count"]
                    )

                await asyncio.sleep(IDLE_SLEEP)

        except Exception:
            await asyncio.sleep(ERROR_SLEEP)


async def start_worker():
    await process_payment_queue(asyncio.Semaphore(1))


async def start_workers(
    num_workers: int = NUM_WORKERS,
    max_concurrent_requests: int = MAX_CONCURRENT_REQUESTS,
):
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    tasks = []
    for i in range(num_workers):
        task = asyncio.create_task(process_payment_queue(semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)

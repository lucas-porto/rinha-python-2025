import orjson
from datetime import datetime
from typing import Optional
from functools import lru_cache

from .redis_pool import redis_client

KEY_SET = "payments_by_date"


@lru_cache(maxsize=1024)
def get_cached_timestamp(dt: datetime) -> float:
    return dt.timestamp()


async def save_payment(cid: str, amount: float, processor: str, requested_at: datetime):
    timestamp = get_cached_timestamp(requested_at)

    payment_json = orjson.dumps(
        {
            "correlationId": cid,
            "amount": amount,
            "processor": processor,
            "requested_at": timestamp,
        }
    ).decode()

    await redis_client.zadd(KEY_SET, {payment_json: timestamp})


async def get_summary(
    ts_from: Optional[datetime] = None, ts_to: Optional[datetime] = None
):
    min_score = ts_from.timestamp() if ts_from else "-inf"
    max_score = ts_to.timestamp() if ts_to else "+inf"

    payments = await redis_client.zrangebyscore(KEY_SET, min_score, max_score)

    summary = {
        "default": {"totalRequests": 0, "totalAmount": 0.0},
        "fallback": {"totalRequests": 0, "totalAmount": 0.0},
    }

    for payment_json in payments:
        p = orjson.loads(payment_json)
        processor = p["processor"]
        amount = p["amount"]

        if processor not in summary:
            summary[processor] = {"totalRequests": 0, "totalAmount": 0.0}

        summary[processor]["totalRequests"] += 1
        summary[processor]["totalAmount"] += amount

    for key in summary:
        summary[key]["totalAmount"] = round(summary[key]["totalAmount"], 1)

    return summary


async def purge_payments():
    await redis_client.delete(KEY_SET)

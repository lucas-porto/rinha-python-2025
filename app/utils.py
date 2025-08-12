import re
import math
import calendar
import orjson
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from app.database.redis_pool import redis_client

ISO_DATE_PATTERN = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{3}))?"
)

DEFAULT_FEE = 0.05
FALLBACK_FEE = 0.15
REDIS_TIMEOUT = 0.2

CHAR_TO_INT = {str(i): i for i in range(10)}


def fast_parse_int(s: str) -> int:
    if not s:
        return 0

    value = 0
    for char in s:
        if char in CHAR_TO_INT:
            value = value * 10 + CHAR_TO_INT[char]
    return value


def iso_to_timestamp(date_string: str) -> Tuple[Optional[str], bool]:
    if not date_string:
        return None, False

    if len(date_string) <= 13 and date_string.isdigit():
        # Se é um timestamp em milissegundos, converter para segundos
        timestamp_ms = fast_parse_int(date_string)
        timestamp_s = timestamp_ms / 1000.0
        return str(timestamp_s), True

    match = ISO_DATE_PATTERN.match(date_string)
    if not match:
        return None, False

    year = fast_parse_int(match.group(1))
    month = fast_parse_int(match.group(2))
    day = fast_parse_int(match.group(3))
    hour = fast_parse_int(match.group(4))
    minute = fast_parse_int(match.group(5))
    second = fast_parse_int(match.group(6))
    milliseconds = fast_parse_int(match.group(7)) if match.group(7) else 0

    # Criar time tuple e converter para timestamp UTC
    time_tuple = (year, month, day, hour, minute, second, 0, 0, 0)
    epoch_seconds = calendar.timegm(time_tuple)
    # Converter para segundos (float) para compatibilidade com Redis
    timestamp_s = epoch_seconds + (milliseconds / 1000.0)

    return str(timestamp_s), True


def round_to_cents(value: float) -> float:
    return math.floor(value * 100 + 0.5) / 100.0


def calculate_fee(amount: float, is_fallback: bool = False) -> float:
    fee_rate = FALLBACK_FEE if is_fallback else DEFAULT_FEE
    fee = amount * fee_rate
    return round_to_cents(fee)


def validate_amount(amount: float) -> bool:
    return isinstance(amount, (int, float)) and amount > 0


def format_timestamp(timestamp_ms: int) -> str:
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    except (ValueError, OSError):
        return str(timestamp_ms)


def safe_parse_int(s: str, default: int = 0) -> int:
    try:
        return fast_parse_int(s)
    except (ValueError, TypeError):
        return default


def is_valid_iso_date(date_string: str) -> bool:
    if not date_string:
        return False

    if date_string.isdigit():
        return len(date_string) <= 13

    return bool(ISO_DATE_PATTERN.match(date_string))


async def get_redis_range(key: str, min_score: str, max_score: str) -> List[bytes]:
    try:
        return await redis_client.zrangebyscore(key, min=min_score, max=max_score)
    except Exception:
        return []


async def calculate_summary(
    items: List[bytes], transaction_type: str
) -> Dict[str, Any]:
    total_amount = 0.0
    transaction_count = 0

    for item in items:
        if not item:
            continue

        try:
            if isinstance(item, (bytes, bytearray)):
                json_string = item.decode("utf-8")
            else:
                json_string = str(item)

            transaction = orjson.loads(json_string)
            amount = float(transaction.get("amount", 0) or 0)

            total_amount += amount
            transaction_count += 1

        except (ValueError, TypeError, orjson.JSONDecodeError):
            continue

    fee_rate = DEFAULT_FEE if transaction_type == "default" else FALLBACK_FEE
    total_fee = total_amount * fee_rate

    return {
        "totalRequests": transaction_count,
        "totalAmount": round_to_cents(total_amount),
        "totalFee": round_to_cents(total_fee),
        "feePerTransaction": fee_rate,
    }

import os

from typing import Optional, Dict, Any

from app.client.session import get_httpx_client


def get_processor_url(processor_type: str, endpoint: str = "payments") -> str:
    base_url = os.getenv(
        f"PROCESSOR_{processor_type.upper()}_URL",
        f"http://payment-processor-{processor_type.lower()}:8080",
    )

    if endpoint == "health":
        return f"{base_url}/payments/service-health"
    return f"{base_url}/payments"


async def process_payment_in_processor(
    payload: Dict[str, Any],
    processor_type: str = "default",
    timeout: Optional[float] = 6.0,  # Timeout adequado para o fallback com 5s de delay
) -> str:
    try:
        client = await get_httpx_client()
        processor_url = get_processor_url(processor_type)

        processor_payload = {
            "correlationId": payload["correlationId"],
            "amount": payload["amount"],
            "requestedAt": payload["requested_at"],
        }
        response = await client.post(
            processor_url, json=processor_payload, timeout=timeout
        )

        if response.status_code == 422:
            return "not avaiable"

        if response.status_code != 200:
            response.raise_for_status()

        return response.text
    except Exception as e:
        raise e


async def get_payment_processor_health(
    processor_type: str = "default", timeout: Optional[float] = 1.5
) -> bool:
    try:
        client = await get_httpx_client()
        health_url = get_processor_url(processor_type, "health")

        response = await client.get(health_url)
        return response.status_code == 200
    except Exception:
        return False




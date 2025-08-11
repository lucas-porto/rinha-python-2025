import httpx
from typing import Optional

# Sessão HTTP
_http_client: Optional[httpx.AsyncClient] = None


async def get_httpx_client() -> httpx.AsyncClient:
    global _http_client

    if _http_client is None:
        limits = httpx.Limits(
            max_keepalive_connections=30, max_connections=30, keepalive_expiry=300.0
        )

        # Timeouts para processamento de pagamentos
        timeout = httpx.Timeout(timeout=3.0, connect=0.5, read=2.0)

        _http_client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers={
                "Connection": "keep-alive",
                "User-Agent": "payment-worker-httpx/1.0",
                "Accept": "application/json",
            },
        )

    return _http_client


async def cleanup_http_client():
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None

#!/usr/bin/env python3
import asyncio
import aiohttp
import json
from datetime import datetime

async def get_backend_summary():
    """Captura o summary do nosso backend"""
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:9999/payments-summary") as response:
            if response.status == 200:
                return await response.json()
    return None

async def get_processor_summary(processor_type):
    """Captura o summary de um payment processor"""
    port = 8001 if processor_type == "default" else 8002
    async with aiohttp.ClientSession() as session:
        headers = {"X-Rinha-Token": "123"}
        async with session.get(f"http://localhost:{port}/admin/payments-summary", headers=headers) as response:
            if response.status == 200:
                return await response.json()
    return None

async def get_redis_count():
    """Captura o total de pagamentos no Redis"""
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    return r.zcard("payments_by_date")

async def main():
    print("=== CAPTURA DE DADOS ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Capturar dados do backend
    backend_data = await get_backend_summary()
    if backend_data:
        backend_total = backend_data["default"]["totalRequests"] + backend_data["fallback"]["totalRequests"]
        print(f"Backend - Total: {backend_total}")
        print(f"Backend - Default: {backend_data['default']['totalRequests']}")
        print(f"Backend - Fallback: {backend_data['fallback']['totalRequests']}")
    
    # Capturar dados dos processors
    default_data = await get_processor_summary("default")
    fallback_data = await get_processor_summary("fallback")
    
    if default_data and fallback_data:
        processor_total = default_data["totalRequests"] + fallback_data["totalRequests"]
        print(f"Processors - Total: {processor_total}")
        print(f"Processors - Default: {default_data['totalRequests']}")
        print(f"Processors - Fallback: {fallback_data['totalRequests']}")
    
    # Capturar dados do Redis
    redis_count = await get_redis_count()
    print(f"Redis - Total: {redis_count}")
    
    # Salvar em arquivo para comparação
    data = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend_data,
        "processors": {
            "default": default_data,
            "fallback": fallback_data
        },
        "redis_count": redis_count
    }
    
    with open("test_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("Dados salvos em test_data.json")

if __name__ == "__main__":
    asyncio.run(main())

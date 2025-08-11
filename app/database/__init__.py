from .redis_pool import redis_client
from .storage import save_payment, get_summary, purge_payments


class Database:
    def __init__(self):
        self.redis_client = redis_client

    async def initialize(self):
        try:
            await self.redis_client.ping()
            print("Database inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar database: {e}")
            raise e


database = Database()

__all__ = ["database", "redis_client", "save_payment", "get_summary", "purge_payments"]

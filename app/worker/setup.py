import asyncio
import signal
import sys
from app.worker.worker import start_workers, NUM_WORKERS, MAX_CONCURRENT_REQUESTS


async def shutdown(signal, loop):
    # print(f"Recebido sinal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def handle_exit(signum, frame):
    # print("Recebido sinal de saída, encerrando workers...")
    sys.exit(0)


async def main():
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )

    signal.signal(signal.SIGINT, handle_exit)

    # print(f"Iniciando {NUM_WORKERS} workers com {MAX_CONCURRENT_REQUESTS} requests concorrentes...")

    try:
        await start_workers(NUM_WORKERS, MAX_CONCURRENT_REQUESTS)
    except KeyboardInterrupt:
        print("Workers interrompidos pelo usuário")
    except Exception as e:
        print(f"Erro nos workers: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

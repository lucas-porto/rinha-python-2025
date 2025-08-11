from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import Response


async def health_check(request: Request) -> Response:
    return Response(status_code=204)


router = [Route("/health", health_check, methods=["GET"])]

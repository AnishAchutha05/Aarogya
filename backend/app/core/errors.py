"""Error handling utilities and exception types."""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AarogyaError(Exception):
    """Base exception for application errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AarogyaError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class ForbiddenError(AarogyaError):
    def __init__(self):
        super().__init__("Access denied", status.HTTP_403_FORBIDDEN)


class ConflictError(AarogyaError):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail, status.HTTP_409_CONFLICT)


class ProviderError(AarogyaError):
    def __init__(self, detail: str = "AI provider error"):
        super().__init__(detail, status.HTTP_502_BAD_GATEWAY)


async def aarogya_exception_handler(
    request: Request, exc: AarogyaError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

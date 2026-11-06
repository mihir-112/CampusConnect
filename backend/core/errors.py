"""One error format for the whole API. Owner: Mihir.

Every error response looks like:
    {"error": {"code": "not_found", "message": "...", "fields": {"title": "..."} or null}}
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("campusconnect")

_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    413: "file_too_large",
    422: "validation_error",
    429: "too_many_attempts",
}


class AppError(Exception):
    def __init__(self, status_code: int, message: str, code: str | None = None, fields: dict | None = None, headers=None):
        self.status_code = status_code
        self.message = message
        self.code = code or _CODES.get(status_code, "error")
        self.fields = fields
        self.headers = headers
        super().__init__(message)

    @classmethod
    def validation(cls, fields: dict | str) -> "AppError":
        if isinstance(fields, str):
            fields = {"form": fields}
        return cls(422, "Please correct the highlighted fields.", "validation_error", fields)

    @classmethod
    def not_found(cls, message: str = "We couldn't find that. It may have been removed or never published.") -> "AppError":
        return cls(404, message)

    @classmethod
    def forbidden(cls, message: str = "You don't have permission to do that.") -> "AppError":
        return cls(403, message)

    @classmethod
    def unauthorized(cls, message: str = "Please log in to continue.") -> "AppError":
        return cls(401, message, headers={"WWW-Authenticate": "Bearer"})


def error_body(code: str, message: str, fields: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "fields": fields}}


def _label(name: str) -> str:
    return name.replace("_", " ").capitalize()


def _field_messages(exc: RequestValidationError) -> dict:
    fields: dict = {}
    for item in exc.errors():
        loc = [str(p) for p in item.get("loc", ()) if p not in ("body", "query", "path", "form")]
        name = loc[0] if loc else "form"
        if item.get("type") == "missing":
            message = f"{_label(name)} is required."
        else:
            message = str(item.get("msg", "Invalid value.")).removeprefix("Value error, ")
        fields.setdefault(name, message)
    return fields


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_request: Request, exc: AppError):
        return JSONResponse(error_body(exc.code, exc.message, exc.fields), status_code=exc.status_code, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _validation(_request: Request, exc: RequestValidationError):
        return JSONResponse(
            error_body("validation_error", "Please correct the highlighted fields.", _field_messages(exc)),
            status_code=422,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_request: Request, exc: StarletteHTTPException):
        message = "We couldn't find that." if exc.status_code == 404 else str(exc.detail)
        return JSONResponse(
            error_body(_CODES.get(exc.status_code, "error"), message), status_code=exc.status_code, headers=getattr(exc, "headers", None)
        )

    @app.exception_handler(Exception)
    async def _unexpected(_request: Request, exc: Exception):
        log.exception("Unhandled error", exc_info=exc)
        return JSONResponse(
            error_body("server_error", "An unexpected error occurred. Please try again in a moment."), status_code=500
        )

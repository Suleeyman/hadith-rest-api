import html
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.schema import ErrorResponse, Resource
from src.core.settings import settings
from src.database import close_mongodb_connection, connect_to_mongodb
from src.exceptions import ResourceNotFoundError
from src.modules.book.router import book_router, edition_book_router
from src.modules.edition.router import router as edition_router
from src.modules.hadith.router import edition_hadith_router, hadith_router

logging.basicConfig(level=logging.INFO)

limiter = Limiter(
    key_func=get_remote_address, default_limits=["7/minute"], enabled=True
)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """
    Manage application lifespan events.

    Connect to MongoDB on startup and close connection on shutdown.
    """
    # Startup: connect to database
    connect_to_mongodb()
    yield
    # Shutdown: close database connection
    close_mongodb_connection()


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    summary=settings.app_summary,
    version=settings.app_version,
    contact=settings.app_contact,
    license_info=settings.app_license,
    lifespan=lifespan,
    openapi_tags=[
        # Make it appear at the top
        {"name": "Root"},
        {"name": Resource.edition},
        {"name": Resource.book},
        {"name": Resource.hadith},
    ],
    docs_url=None,
    redoc_url=None,
)

app.state.limiter = limiter
"""
Types are not well supported at the moment
"""
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # ty:ignore[invalid-argument-type]

app.add_middleware(SlowAPIMiddleware)  # ty:ignore[invalid-argument-type]


app.include_router(router=edition_router)
app.include_router(router=book_router)
app.include_router(edition_book_router)
app.include_router(router=hadith_router)
app.include_router(edition_hadith_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    message = "Validation error"
    details = {}
    for error in exc.errors():
        loc = error["loc"]
        max_length = error.get("ctx", {}).get("max_length", 64)
        got = "nothing"
        if error["input"] is not None:
            got = (
                error["input"]
                if len(error["input"]) <= max_length
                else error["input"][:max_length] + "..."
            )
        details[loc[1]] = f"{error['msg']} (got {got})."
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            code=status.HTTP_400_BAD_REQUEST,
            message=message,
            details=details,
        ).model_dump(),
    )


@app.exception_handler(ResourceNotFoundError)
def exception_404_handler(_request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            code=status.HTTP_404_NOT_FOUND, message=exc.message, details=exc.details
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def internal_exception_handler(_request: Request, _exc: Exception):
    """Handle uncaught exceptions and return a standardized 500 error response."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle FastAPI default 404 Not Found or fallback to default."""
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                code=status.HTTP_404_NOT_FOUND,
                message="Resource not found",
                details={"path": html.escape(request.url.path)},
            ).model_dump(),
        )

    # For other HTTP exceptions, fallback to default behavior
    return await http_exception_handler(request, exc)


@app.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=settings.app_name + " — Swagger",
        swagger_favicon_url="/favicon.png",
    )


@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=settings.app_name + " — Redocly",
        redoc_favicon_url="/favicon.png",
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/favicon.png", include_in_schema=False)
async def favicon_png():
    return FileResponse("static/favicon.png")


@app.get(
    "/",
    tags=["Root"],
    summary="General API information",
    description="Returns general information about the API, including links to the GitHub repository, Supporting URL, Swagger UI documentation and ReDoc documentation.",
)
@limiter.exempt
async def root(_request: Request):
    return {
        "title": "Multilingual REST API of Popular Hadith Editions — Hadislam",
        "github_url": "https://github.com/Suleeyman/hadith-rest-api",
        "support": "https://ko-fi.com/ysuleyman",
        "swagger": "/docs",
        "redocly": "/redoc",
    }


# https://github.com/fastapi/fastapi/discussions/6695#discussioncomment-8401703
for method_item in app.openapi().get("paths", {}).values():
    for param in method_item.values():
        responses = param.get("responses")
        if "422" in responses:
            del responses["422"]

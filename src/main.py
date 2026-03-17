import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.core.settings import settings
from src.database import close_mongodb_connection, connect_to_mongodb
from src.exceptions import ResourceNotFoundError
from src.modules.book.router import book_router, edition_book_router
from src.modules.common.model import ErrorResponse, Resource
from src.modules.edition.router import router as edition_router

logging.basicConfig(level=logging.INFO)


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
)


app.include_router(router=edition_router)
app.include_router(router=book_router)
app.include_router(edition_book_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    message = "Validation error"
    details = {}
    for error in exc.errors():
        loc = error["loc"]
        max_length = error.get("ctx", {}).get("max_length", 64)
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


@app.get(
    "/",
    tags=["Root"],
    summary="General API information",
    description="Returns general information about the API, including links to the GitHub repository, Supporting URL, Swagger UI documentation and ReDoc documentation.",
)
async def root():
    return {
        "title": "Multilingual REST API of Popular Hadith Editions — Hadislam",
        "github_url": "https://github.com/Suleeyman/hadislam.org",
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

from fastapi import APIRouter

from src.core.openapi.openapi_response_annotation import (
    invalid_request_annotation,
    not_found_response_annotation,
    not_found_responses_annotation,
)
from src.modules.book.dependencies import BookIndex, BookServiceDepends
from src.modules.book.dto.book_with_edition import BookWithEdition
from src.modules.book.model import Book
from src.modules.common.model import PyObjectId, Resource
from src.modules.edition.dependencies import EditionBySlugDepends

book_router = APIRouter(
    prefix="/books",
    tags=[Resource.book],
)


@book_router.get("/", response_model=list[Book])
def list_books(service: BookServiceDepends):
    """Get a list of books."""
    return service.get_books()


@book_router.get(
    "/{book_id}",
    response_model=BookWithEdition,
    responses={
        404: not_found_response_annotation(Resource.book),
        400: invalid_request_annotation("Invalid Book Id Format"),
    },
)
def get_book_by_id(book_id: PyObjectId, service: BookServiceDepends):
    return service.get_book_by_id(book_id)


edition_book_router = APIRouter(prefix="/editions", tags=["Book"])


"""
FAST003 : https://github.com/astral-sh/ruff/issues/21075
"""


@edition_book_router.get(
    "/{slug}/books",  # noqa: FAST003
    response_model=list[Book],
    responses={
        404: not_found_response_annotation(Resource.edition),
        400: invalid_request_annotation("Invalid Edition Slug Format"),
    },
)
def list_books_by_edition_slug(
    edition: EditionBySlugDepends,
    book_service: BookServiceDepends,
):
    return book_service.get_books_by_edition_id(edition.id)


@edition_book_router.get(
    "/{slug}/books/{book_index}",  # noqa: FAST003
    response_model=BookWithEdition,
    responses={
        404: not_found_responses_annotation(Resource.book, Resource.edition),
        400: invalid_request_annotation("Invalid Edition Slug or Book Index Format"),
    },
)
def get_book_by_edition_slug_and_book_index(
    edition: EditionBySlugDepends,
    book_index: BookIndex,
    book_service: BookServiceDepends,
):
    return book_service.get_book_by_edition_and_index(edition.id, book_index)

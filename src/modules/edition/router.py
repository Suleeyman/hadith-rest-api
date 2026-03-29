from fastapi import APIRouter

from src.core.dependencies import ManyLanguageSelectionDepends
from src.core.openapi.openapi_response_annotation import (
    invalid_request_annotation,
    not_found_response_annotation,
)
from src.core.schema import Resource
from src.modules.edition.dependencies import (
    EditionServiceDepends,
    EditionSlug,
    FilterByAvailableLanguage,
)
from src.modules.edition.dto.edition_with_books import EditionWithBooks
from src.modules.edition.model import Edition

router = APIRouter(
    prefix="/editions",
    tags=[Resource.edition],
)


@router.get("/", response_model=list[Edition])
def list_editions(
    service: EditionServiceDepends,
    languages: ManyLanguageSelectionDepends,
    available: FilterByAvailableLanguage = None,
):
    """Get a list of editions."""
    return service.get_editions(languages, available_language=available)


@router.get(
    "/{slug}",
    response_model=EditionWithBooks,
    responses={
        404: not_found_response_annotation(Resource.edition),
        400: invalid_request_annotation("Invalid Edition Slug Format"),
    },
)
def get_edition_by_slug(
    slug: EditionSlug,
    service: EditionServiceDepends,
    languages: ManyLanguageSelectionDepends,
):
    """Get a specific edition by slug."""
    return service.get_edition_by_slug_join_books(slug.lower(), languages)

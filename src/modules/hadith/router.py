from fastapi import APIRouter

from src.core.dependencies import (
    LanguageQuery,
    ManyLanguageSelectionDepends,
    SearchQueryDepends,
)
from src.core.language import Language
from src.core.openapi.openapi_response_annotation import (
    invalid_request_annotation,
    not_found_response_annotation,
    not_found_responses_annotation,
)
from src.core.pagination import PaginationParamsDepends, PaginationSmallParamsDepends
from src.core.schema import PaginatedResponse, PyObjectId, Resource
from src.modules.book.dependencies import BookIndex
from src.modules.edition.dependencies import EditionBySlugDepends
from src.modules.hadith.dependencies import (
    BookHadithIndex,
    EditionIdDepends,
    FilterHadithQueryDepends,
    HadithIndex,
    HadithIndexMinor,
    HadithServiceDepends,
)
from src.modules.hadith.dto.hadith_response import (
    HadithJoinedEditionAndBook,
    HadithSearchItem,
    HadithWithVariants,
)
from src.modules.hadith.model import Hadith

hadith_router = APIRouter(
    prefix="/hadiths",
    tags=[Resource.hadith],
)


@hadith_router.get(
    "/",
    response_model=PaginatedResponse[Hadith],
    responses={
        400: invalid_request_annotation(),
    },
)
def list_hadiths(
    pagination: PaginationParamsDepends,
    filter_query: FilterHadithQueryDepends,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
):
    return service.get_hadiths_paginated(
        page=pagination.page,
        page_size=pagination.page_size,
        filter_query=filter_query,
        languages=languages,
    )


@hadith_router.get(
    "/search",
    response_model=PaginatedResponse[HadithSearchItem],
    responses={
        400: invalid_request_annotation(),
    },
)
def search_hadiths(  # noqa: PLR0913
    q: SearchQueryDepends,
    pagination: PaginationSmallParamsDepends,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
    search_lang: LanguageQuery = Language.en,
    edition: EditionIdDepends = None,
):
    return service.search_hadiths(
        q=q,
        lang=search_lang,
        languages=languages,
        pagination=pagination,
        edition=edition,
    )


@hadith_router.get(
    "/{hadith_id}",
    response_model=HadithJoinedEditionAndBook,
    responses={
        404: not_found_response_annotation(Resource.hadith),
        400: invalid_request_annotation(),
    },
)
def get_hadith_by_id(
    hadith_id: PyObjectId,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
):
    return service.get_hadith_by_id(hadith_id, languages)


edition_hadith_router = APIRouter(prefix="/editions", tags=[Resource.hadith])


"""
FAST003 : https://github.com/astral-sh/ruff/issues/21075
"""


@edition_hadith_router.get(
    "/{slug}/hadiths",  # noqa: FAST003
    response_model=PaginatedResponse[Hadith],
    responses={
        404: not_found_response_annotation(Resource.edition),
        400: invalid_request_annotation(),
    },
)
def list_hadiths_by_edition_slug(
    edition: EditionBySlugDepends,
    pagination: PaginationParamsDepends,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
):
    return service.get_hadiths_by_edition_paginated(
        edition_id=edition.id,
        page=pagination.page,
        page_size=pagination.page_size,
        languages=languages,
    )


@edition_hadith_router.get(
    "/{slug}/hadiths/{hadith_index}.{hadith_index_minor}",  # noqa: FAST003
    response_model=Hadith,
    responses={
        404: not_found_responses_annotation(Resource.hadith, Resource.edition),
        400: invalid_request_annotation("Invalid Edition Slug or Hadith Index Format"),
    },
)
def get_hadith_variant_by_index(
    edition: EditionBySlugDepends,
    hadith_index: HadithIndex,
    hadith_index_minor: HadithIndexMinor,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
):
    return service.get_hadith_variant_by_edition_and_index_minor(
        edition_id=edition.id,
        hadith_index=hadith_index,
        hadith_index_minor=hadith_index_minor,
        languages=languages,
    )


# Must appear after the above endpoint for parser
@edition_hadith_router.get(
    "/{slug}/hadiths/{hadith_index}",  # noqa: FAST003
    response_model=HadithWithVariants,
    responses={
        404: not_found_responses_annotation(Resource.hadith, Resource.edition),
        400: invalid_request_annotation("Invalid Edition Slug or Hadith Index Format"),
    },
)
def get_hadith_by_index(
    edition: EditionBySlugDepends,
    hadith_index: HadithIndex,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
):
    return service.get_hadith_by_edition_and_index(
        edition_id=edition.id, hadith_index=hadith_index, languages=languages
    )


@edition_hadith_router.get(
    "/{slug}/books/{book_index}/hadiths",  # noqa: FAST003
    response_model=PaginatedResponse[Hadith],
    responses={
        404: not_found_response_annotation(Resource.edition),
        400: invalid_request_annotation("Invalid Edition Slug or Book Index Format"),
    },
)
def list_hadiths_by_book(
    edition: EditionBySlugDepends,
    book_index: BookIndex,
    pagination: PaginationParamsDepends,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
):
    return service.get_hadiths_by_edition_and_book_paginated(
        edition_id=edition.id,
        book_index=book_index,
        page=pagination.page,
        page_size=pagination.page_size,
        languages=languages,
    )


@edition_hadith_router.get(
    "/{slug}/books/{book_index}/hadiths/{book_hadith_index}",  # noqa: FAST003
    response_model=Hadith,
    responses={
        404: not_found_responses_annotation(Resource.hadith, Resource.edition),
        400: invalid_request_annotation("Invalid Edition Slug or Book Index Format"),
    },
)
def get_hadith_by_book_index(
    edition: EditionBySlugDepends,
    book_index: BookIndex,
    book_hadith_index: BookHadithIndex,
    languages: ManyLanguageSelectionDepends,
    service: HadithServiceDepends,
):
    return service.get_hadith_by_edition_book_and_index(
        edition_id=edition.id,
        book_index=book_index,
        book_hadith_index=book_hadith_index,
        languages=languages,
    )

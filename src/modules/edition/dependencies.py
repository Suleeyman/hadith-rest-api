from typing import Annotated

from fastapi import Depends, Path, Query
from pymongo.database import Database

from src.core.language import Language
from src.core.schema import PyObjectId
from src.database import get_database
from src.modules.edition.model import Edition
from src.modules.edition.repository import EditionRepository
from src.modules.edition.service import EditionService

"""
Values
"""
EditionSlug = Annotated[
    str,
    Path(
        min_length=1,
        max_length=64,
        description="Hyphen separated latinized english edition name",
    ),
]

FilterByAvailableLanguage = Annotated[
    Language | None,
    Query(
        description="Filter by available language",
        examples=[Language.fr],
    ),
]

"""
Objects
"""


def get_edition_repository(
    db: Annotated[Database, Depends(get_database)],
) -> EditionRepository:
    return EditionRepository(db)


EditionRepositoryDepends = Annotated[EditionRepository, Depends(get_edition_repository)]


def get_edition_service(
    repo: EditionRepositoryDepends,
) -> EditionService:
    """Dependency to get edition service instance."""
    return EditionService(repo)


EditionServiceDepends = Annotated[EditionService, Depends(get_edition_service)]


def get_edition_by_id(
    edition_id: PyObjectId,
    service: EditionServiceDepends,
):
    return service.get_edition_by_id(edition_id)


EditionByIdDepends = Annotated[Edition, Depends(get_edition_by_id)]


def get_edition_by_slug(slug: EditionSlug, service: EditionServiceDepends) -> Edition:
    return service.get_edition_by_slug(slug)


EditionBySlugDepends = Annotated[Edition, Depends(get_edition_by_slug)]

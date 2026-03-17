from typing import Annotated

from fastapi import Depends, Path
from pymongo.database import Database

from src.database import get_database
from src.modules.common.model import PyObjectId
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

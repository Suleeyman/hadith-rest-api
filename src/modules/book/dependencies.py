from typing import Annotated

from fastapi import Depends, Path, Query
from pymongo.database import Database

from src.core.schema import PyObjectId
from src.database import get_database
from src.modules.book.repository import BookRepository
from src.modules.book.schema import FilterBooksQueries
from src.modules.book.service import BookService

"""
Objects
"""


def get_book_repository(
    db: Annotated[Database, Depends(get_database)],
) -> BookRepository:
    return BookRepository(db)


BookRepositoryDepends = Annotated[BookRepository, Depends(get_book_repository)]


def get_book_service(
    repo: BookRepositoryDepends,
) -> BookService:
    """Dependency to get book service instance."""
    return BookService(repo)


BookServiceDepends = Annotated[BookService, Depends(get_book_service)]


def get_filter_queries(
    edition: Annotated[
        PyObjectId | None,
        Query(description="Edition Id", examples=["69b55e8d6f42ba7ccb2a131d"]),
    ] = None,
) -> FilterBooksQueries:
    return FilterBooksQueries(edition=edition)


FilterBooksQueryDepends = Annotated[FilterBooksQueries, Depends(get_filter_queries)]


"""
Values
"""
BookIndex = Annotated[
    int,
    Path(ge=0, le=128, description="Book index as it appears in the Edition"),
]

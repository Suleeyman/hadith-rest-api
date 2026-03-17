from typing import Annotated

from fastapi import Depends, Path
from pymongo.database import Database

from src.database import get_database
from src.modules.book.repository import BookRepository
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


"""
Values
"""
BookIndex = Annotated[
    int,
    Path(ge=1, le=128, description="Book index as it appears in the Edition"),
]

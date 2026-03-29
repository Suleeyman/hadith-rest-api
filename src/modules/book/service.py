from typing import Any

from bson import ObjectId

from src.core.schema import PyObjectId
from src.modules.book.dto.book_with_edition import BookWithEdition
from src.modules.book.exception import BookNotFoundError
from src.modules.book.model import Book
from src.modules.book.repository import BookRepository
from src.modules.book.schema import FilterBooksQueries


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def get_books(
        self,
    ) -> list[Book]:
        return list(self.repository.find_all())

    def get_books_paginated(
        self,
        page: int,
        page_size: int,
        filter_query: FilterBooksQueries,
        languages: list[str],
    ) -> dict[str, Any]:
        return self.repository.paginate(
            page=page,
            page_size=page_size,
            filter_query=filter_query.to_mongo(),
            languages=languages,
        )

    def get_book_by_id(
        self, book_id: PyObjectId, languages: list[str]
    ) -> BookWithEdition:
        book = self.repository.find_one_by_id_join_edition(ObjectId(book_id), languages)

        if book is None:
            raise BookNotFoundError(book_id)

        return BookWithEdition(**book)

    def get_books_by_edition_id(
        self, edition_id: PyObjectId, languages: list[str]
    ) -> list[Book]:
        return list(
            self.repository.find_with_edition_id(
                ObjectId(edition_id), languages=languages
            )
        )

    def get_book_by_edition_and_index(
        self, edition_id: PyObjectId, book_index: int, languages: list[str]
    ) -> BookWithEdition:
        book = self.repository.find_one_by_book_index_with_edition_id_join_edition(
            book_index, ObjectId(edition_id), languages=languages
        )

        if book is None:
            identifier = f"{edition_id}:{book_index}"
            raise BookNotFoundError(identifier)

        return BookWithEdition(**book)

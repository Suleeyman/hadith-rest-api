from src.modules.book.model import Book
from src.modules.edition.model import Edition


class EditionWithBooks(Edition):
    books: list[Book]

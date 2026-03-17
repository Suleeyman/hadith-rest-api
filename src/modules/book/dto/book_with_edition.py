from src.modules.book.model import Book
from src.modules.edition.model import Edition


class BookWithEdition(Book):
    edition: Edition

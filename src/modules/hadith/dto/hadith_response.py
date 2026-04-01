from src.modules.book.model import Book
from src.modules.edition.model import Edition
from src.modules.hadith.model import Hadith


class HadithWithVariants(Hadith):
    variants: list[Hadith] | None = None


class HadithJoinedEditionAndBook(Hadith):
    edition: Edition | None = None
    book: Book | None = None


class HadithSearchItem(HadithJoinedEditionAndBook):
    score: float

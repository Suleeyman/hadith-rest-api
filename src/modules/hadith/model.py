from pydantic import BaseModel, Field

from src.core.schema import PyObjectId


class Grade(BaseModel):
    name: str
    grade: str


class Hadith(BaseModel):
    id: PyObjectId = Field(alias="_id")
    edition_id: PyObjectId = Field(alias="editionId")
    book_index: int = Field(alias="bookIndex")
    hadith_index: int = Field(alias="hadithIndex")
    hadith_index_minor: int | None = Field(alias="hadithIndexMinor")
    book_hadith_index: int = Field(alias="bookHadithIndex")
    text: dict[str, str]  # e.g., {"ar": "...", "en": "...", etc.}
    grades: list[Grade]

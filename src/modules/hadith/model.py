from pydantic import BaseModel, ConfigDict, Field
from pydantic.v1.utils import to_lower_camel

from src.core.language import Language
from src.core.schema import PyObjectId


class Grade(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    grade: str


class Hadith(BaseModel):
    model_config = ConfigDict(alias_generator=to_lower_camel, frozen=True)

    id: PyObjectId = Field(alias="_id")
    edition_id: PyObjectId
    book_index: int
    hadith_index: int
    hadith_index_minor: int | None
    book_hadith_index: int
    text: dict[Language, str]  # e.g., {"ar": "...", "en": "...", etc.}
    grades: list[Grade]

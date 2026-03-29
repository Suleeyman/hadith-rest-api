from pydantic import BaseModel, ConfigDict, Field
from pydantic.v1.utils import to_lower_camel

from src.core.language import Language
from src.core.schema import PyObjectId


class Book(BaseModel):
    model_config = ConfigDict(alias_generator=to_lower_camel, frozen=True)

    id: PyObjectId = Field(alias="_id")
    edition_id: PyObjectId
    name: dict[Language, str]  # e.g., {"en": "Forty Hadith of Shah Waliullah Dehlawi"}
    book_index: int
    hadith_count: int
    hadith_index_start: int

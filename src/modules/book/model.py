from pydantic import BaseModel, Field

from src.modules.common.model import PyObjectId


class Book(BaseModel):
    id: PyObjectId = Field(alias="_id")
    edition_id: PyObjectId = Field(alias="editionId")
    name: dict[str, str]  # e.g., {"en": "Forty Hadith of Shah Waliullah Dehlawi"}
    book_index: int = Field(alias="bookIndex")
    hadith_count: int = Field(alias="hadithCount")
    hadith_index_start: int = Field(alias="hadithIndexStart")

from pydantic import BaseModel, Field

from src.modules.common.model import PyObjectId


class Edition(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: dict[str, str]  # e.g., {"en": "Forty Hadith of Shah Waliullah Dehlawi"}
    slug: str
    hadith_count: int = Field(alias="hadithCount")
    book_count: int = Field(alias="bookCount")

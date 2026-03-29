from pydantic import BaseModel, ConfigDict, Field
from pydantic.v1.utils import to_lower_camel

from src.core.language import Language
from src.core.schema import PyObjectId


class Edition(BaseModel):
    model_config = ConfigDict(alias_generator=to_lower_camel, frozen=True)

    id: PyObjectId = Field(alias="_id")
    available_languages: list[Language]
    name: dict[Language, str]  # e.g., {"en": "Forty Hadith of Shah Waliullah Dehlawi"}
    slug: str
    hadith_count: int
    book_count: int

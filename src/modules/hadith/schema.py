from typing import Any

from bson import ObjectId
from pydantic import BaseModel

from src.core.schema import PyObjectId


class FilterHadithQueries(BaseModel):
    edition: PyObjectId | None = None
    book_index: int | None = None

    def to_mongo(self) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if self.edition:
            query["editionId"] = ObjectId(self.edition)
        if self.book_index is not None:
            query["bookIndex"] = self.book_index
        return query

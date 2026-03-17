from typing import Any

from bson import ObjectId
from pydantic import BaseModel

from src.core.schema import PyObjectId


class FilterBooksQueries(BaseModel):
    edition: PyObjectId | None

    def to_mongo(self) -> dict[str, Any]:
        query = {}
        if self.edition:
            query["editionId"] = ObjectId(self.edition)
        return query

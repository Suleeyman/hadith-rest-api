from collections.abc import Iterable
from typing import Any

from bson import ObjectId
from pymongo.database import Database


class HadithRepository:
    def __init__(self, database: Database):
        self.collection = database["hadith"]

    def paginate(
        self,
        page: int,
        page_size: int,
        filter_query: dict[str, Any] | None = None,
        projection: dict[str, int] | None = None,
        sort: Iterable[tuple[str, int]] | None = None,
    ) -> dict[str, Any]:
        query = filter_query if filter_query is not None else {}
        skip = (page - 1) * page_size

        total = self.collection.count_documents(query)
        cursor = self.collection.find(query, projection)
        if sort:
            cursor = cursor.sort(list(sort))
        items = list(cursor.skip(skip).limit(page_size))

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }

    def find_one(
        self, filter_query: dict[str, Any], projection: dict[str, int] | None = None
    ) -> dict[str, Any] | None:
        return self.collection.find_one(filter_query, projection)

    def find_many(
        self,
        filter_query: dict[str, Any],
        projection: dict[str, int] | None = None,
        sort: Iterable[tuple[str, int]] | None = None,
    ) -> list[dict[str, Any]]:
        cursor = self.collection.find(filter_query, projection)
        if sort:
            cursor = cursor.sort(list(sort))
        return list(cursor)

    def find_one_by_id(
        self, document_id: ObjectId, projection: dict[str, int] | None = None
    ) -> dict[str, Any] | None:
        return self.collection.find_one({"_id": document_id}, projection)

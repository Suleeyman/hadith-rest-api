from collections.abc import Iterable
from typing import Any

from bson import ObjectId
from pymongo.database import Database

from src.core.language import build_text_projection


class HadithRepository:
    def __init__(self, database: Database):
        self.collection = database["hadith"]

    def _projection_for_languages(self, languages: list[str]) -> dict[str, int]:
        projection = {
            "_id": 1,
            "editionId": 1,
            "bookIndex": 1,
            "hadithIndex": 1,
            "hadithIndexMinor": 1,
            "bookHadithIndex": 1,
            "grades": 1,
        }
        if "*" in languages:
            projection.update({"text": 1})
            return projection
        projection.update(build_text_projection(languages))
        return projection

    def _filter_languages_expr(self, languages: list[str], field: str) -> Any:
        if "*" in languages:
            return field

        return {
            "$arrayToObject": {
                "$filter": {
                    "input": {"$objectToArray": field},
                    "as": "item",
                    "cond": {"$in": ["$$item.k", languages]},
                }
            }
        }

    def _build_random_pipeline(
        self,
        lang: str,
        edition: ObjectId | None,
        size: str | None,
    ) -> list[dict]:

        pipeline: list[dict] = []

        # 🔹 1. Filter (édition + langue existante)
        match_stage: dict[str, Any] = {f"text.{lang}": {"$exists": True, "$ne": None}}

        if edition is not None:
            match_stage["editionId"] = edition

        pipeline.append({"$match": match_stage})

        # 🔹 2. Compute length (safe)
        pipeline.append(
            {
                "$addFields": {
                    "length": {"$strLenCP": {"$ifNull": [f"$text.{lang}", ""]}}
                }
            }
        )

        # 🔹 3. Filter by size
        if size and size != "*":
            if size == "short":
                pipeline.append({"$match": {"length": {"$lt": 300, "$gt": 15}}})
            elif size == "medium":
                pipeline.append({"$match": {"length": {"$gte": 300, "$lt": 800}}})
            elif size == "long":
                pipeline.append({"$match": {"length": {"$gte": 800}}})

        # 🔹 4. Random
        pipeline.append({"$sample": {"size": 1}})

        # 🔹 5. Lookup edition (OPTIMIZED)
        pipeline.append(
            {
                "$lookup": {
                    "from": "edition",
                    "let": {"id": "$editionId"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$_id", "$$id"]}}},
                        {
                            "$project": {
                                "_id": 1,
                                "availableLanguages": 1,
                                "slug": 1,
                                "hadithCount": 1,
                                "bookCount": 1,
                                f"name.{lang}": 1,
                            }
                        },
                    ],
                    "as": "edition",
                }
            }
        )

        pipeline.append(
            {"$unwind": {"path": "$edition", "preserveNullAndEmptyArrays": True}}
        )

        # 🔹 6. Lookup book (composite key)
        pipeline.append(
            {
                "$lookup": {
                    "from": "book",
                    "let": {
                        "editionId": "$editionId",
                        "bookIndex": "$bookIndex",
                    },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$editionId", "$$editionId"]},
                                        {"$eq": ["$bookIndex", "$$bookIndex"]},
                                    ]
                                }
                            }
                        },
                        {
                            "$project": {
                                "_id": 1,
                                "slug": 1,
                                "editionId": 1,
                                "hadithCount": 1,
                                "bookIndex": 1,
                                "hadithIndexStart": 1,
                                f"name.{lang}": 1,
                            }
                        },
                    ],
                    "as": "book",
                }
            }
        )

        pipeline.append(
            {"$unwind": {"path": "$book", "preserveNullAndEmptyArrays": True}}
        )

        # 🔹 7. Final projection (clean nulls)
        pipeline.append(
            {
                "$project": {
                    "_id": 1,
                    "editionId": 1,
                    "bookIndex": 1,
                    "hadithIndex": 1,
                    "hadithIndexMinor": 1,
                    "bookHadithIndex": 1,
                    f"text.{lang}": 1,
                    "grades": 1,
                    "score": {"$meta": "searchScore"},
                    "edition": 1,
                    "book": 1,
                }
            }
        )

        return pipeline

    def _aggregate_one(self, pipeline: list[dict[str, Any]]):
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

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

    def find_random_hadith(self, lang: str, edition: str | None, size: str):
        pipeline = self._build_random_pipeline(
            lang=lang,
            edition=ObjectId(edition) if edition else None,
            size=size,
        )
        result = list(self.collection.aggregate(pipeline))

        return result

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

    def find_one_with_lookup(self, pipeline: list[dict]) -> dict[str, Any] | None:
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def search(self, pipeline: list[dict[str, Any]]) -> dict[str, Any]:
        result = self._aggregate_one(pipeline)
        return result or {"items": [], "total": 0}

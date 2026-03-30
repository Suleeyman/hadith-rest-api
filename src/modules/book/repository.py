from typing import Any

from bson import ObjectId
from pymongo.database import Database

from src.core.language import build_name_projection
from src.core.pagination import paginate_collection


class BookRepository:
    def __init__(self, database: Database):
        self.collection = database["book"]

    # -------- INTERNAL (DRY) --------

    def _projection_for_languages(self, languages: list[str]) -> dict[str, int]:
        projection = {
            "_id": 1,
            "slug": 1,
            "editionId": 1,
            "hadithCount": 1,
            "bookIndex": 1,
            "hadithIndexStart": 1,
        }
        if "*" in languages:
            projection.update({"name": 1})
            return projection
        projection.update(build_name_projection(languages))
        return projection

    def _lookup_edition(self):
        return [
            {
                "$lookup": {
                    "from": "edition",
                    "localField": "editionId",
                    "foreignField": "_id",
                    "as": "edition",
                }
            },
            {"$unwind": "$edition"},
        ]

    def _aggregate_one(self, pipeline):
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def _aggregate_many(self, pipeline):
        return list(self.collection.aggregate(pipeline))

    # ----- BASIC FIND -----

    def find_all(self):
        return list(self.collection.find({}))

    def paginate(
        self,
        page: int,
        page_size: int,
        filter_query: dict[str, Any],
        languages: list[str],
    ) -> dict[str, Any]:
        projection = self._projection_for_languages(languages)
        return paginate_collection(
            collection=self.collection,
            page=page,
            page_size=page_size,
            filter_query=filter_query,
            projection=projection,
        )

    def find_one_by_id(self, document_id: ObjectId):
        return self.collection.find_one({"_id": document_id})

    def find_with_edition_id(self, edition_id: ObjectId, languages: list[str]):
        projection = self._projection_for_languages(languages)
        return self.collection.find({"editionId": edition_id}, projection)

    def find_one_by_book_index_with_edition_id(
        self, book_index: int, edition_id: ObjectId
    ):
        return self.collection.find_one(
            {"editionId": edition_id, "bookIndex": book_index}
        )

    # ----- LOOKUP FIND -----

    def find_all_join_edition(self):
        pipeline = self._lookup_edition()
        return self._aggregate_many(pipeline)

    def find_one_by_id_join_edition(self, document_id: ObjectId, languages: list[str]):
        if "*" in languages:
            pipeline = [{"$match": {"_id": document_id}}, *self._lookup_edition()]
            return self._aggregate_one(pipeline)

        projection = self._projection_for_languages(languages)
        pipeline = [
            {"$match": {"_id": document_id}},
            *self._lookup_edition(),
            {
                "$project": {
                    **projection,
                    "edition": {
                        "_id": "$edition._id",
                        "availableLanguages": "$edition.availableLanguages",
                        "slug": "$edition.slug",
                        "hadithCount": "$edition.hadithCount",
                        "bookCount": "$edition.bookCount",
                        "name": {lang: f"$edition.name.{lang}" for lang in languages},
                    },
                }
            },
        ]
        return self._aggregate_one(pipeline)

    def find_with_edition_id_join_edition(self, edition_id: ObjectId):
        pipeline = [{"$match": {"editionId": edition_id}}, *self._lookup_edition()]
        return self._aggregate_many(pipeline)

    def find_one_by_book_index_with_edition_id_join_edition(
        self, book_index: int, edition_id: ObjectId, languages: list[str]
    ):
        if "*" in languages:
            pipeline = [
                {
                    "$match": {
                        "editionId": edition_id,
                        "bookIndex": book_index,
                    }
                },
                *self._lookup_edition(),
            ]
            return self._aggregate_one(pipeline)
        projection = self._projection_for_languages(languages)
        pipeline = [
            {
                "$match": {
                    "editionId": edition_id,
                    "bookIndex": book_index,
                }
            },
            *self._lookup_edition(),
            {
                "$project": {
                    **projection,
                    "edition": {
                        "_id": "$edition._id",
                        "availableLanguages": "$edition.availableLanguages",
                        "slug": "$edition.slug",
                        "hadithCount": "$edition.hadithCount",
                        "bookCount": "$edition.bookCount",
                        "name": {lang: f"$edition.name.{lang}" for lang in languages},
                    },
                }
            },
        ]
        return self._aggregate_one(pipeline)

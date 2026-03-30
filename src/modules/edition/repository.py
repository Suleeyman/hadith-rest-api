from bson import ObjectId
from pymongo.database import Database

from src.core.language import build_name_projection


class EditionRepository:
    def __init__(self, database: Database):
        self.collection = database["edition"]

    # -------- INTERNAL (DRY) --------

    def _projection_for_languages(self, languages: list[str]) -> dict[str, int]:
        projection = {
            "_id": 1,
            "availableLanguages": 1,
            "slug": 1,
            "hadithCount": 1,
            "bookCount": 1,
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
                    "from": "book",
                    "localField": "_id",
                    "foreignField": "editionId",
                    "as": "books",
                }
            }
        ]

    def _aggregate_one(self, pipeline):
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def _aggregate_many(self, pipeline):
        return list(self.collection.aggregate(pipeline))

    # ----- BASIC FIND -----

    def find_all(self, languages: list[str], available_language: str | None):
        projection = self._projection_for_languages(languages)

        query = {}
        if available_language is not None:
            query["availableLanguages"] = available_language  # simpler than $in
        return list(self.collection.find(query, projection))

    def find_one_by_id(self, document_id: ObjectId):
        return self.collection.find_one({"_id": document_id})

    def find_one_by_slug(self, slug: str):
        return self.collection.find_one({"slug": slug})

    # ----- LOOKUP FIND -----
    def find_one_by_slug_join_books(self, slug: str, languages: list[str]):
        if "*" in languages:
            pipeline = [{"$match": {"slug": slug}}, *self._lookup_edition()]
            return self._aggregate_one(pipeline)

        projection = self._projection_for_languages(languages)

        pipeline = [
            {"$match": {"slug": slug}},
            *self._lookup_edition(),
            {
                "$project": {
                    **projection,
                    "books": {
                        "$map": {
                            "input": "$books",
                            "as": "book",
                            "in": {
                                "_id": "$$book._id",
                                "slug": "$$book.slug",
                                "editionId": "$$book.editionId",
                                "hadithCount": "$$book.hadithCount",
                                "bookIndex": "$$book.bookIndex",
                                "hadithIndexStart": "$$book.hadithIndexStart",
                                # apply language projection to book.name
                                "name": {
                                    lang: f"$$book.name.{lang}" for lang in languages
                                },
                            },
                        }
                    },
                }
            },
        ]

        return self._aggregate_one(pipeline)

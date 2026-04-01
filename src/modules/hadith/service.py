from typing import Any, Literal

from bson import ObjectId

from src.core.language import build_text_projection
from src.core.schema import PaginationParams, PyObjectId
from src.modules.hadith.exception import HadithNotFoundError
from src.modules.hadith.repository import HadithRepository
from src.modules.hadith.schema import FilterHadithQueries


class HadithService:
    def __init__(self, repository: HadithRepository):
        self.repository = repository

    def _build_get_by_id_pipeline(
        self, hadith_id: ObjectId, languages: list[str]
    ) -> list[dict[str, Any]]:
        return [
            {"$match": {"_id": hadith_id}},
            # 🔹 Edition lookup
            {
                "$lookup": {
                    "from": "edition",
                    "let": {"id": "$editionId"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$_id", "$$id"]}}},
                        {
                            "$project": {
                                "_id": 1,
                                "slug": 1,
                                "availableLanguages": 1,
                                "hadithCount": 1,
                                "bookCount": 1,
                                "name": self._filter_languages_expr(languages, "$name"),
                            }
                        },
                    ],
                    "as": "edition",
                }
            },
            {"$unwind": {"path": "$edition", "preserveNullAndEmptyArrays": True}},
            # 🔹 Book lookup
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
                                "bookIndex": 1,
                                "hadithCount": 1,
                                "hadithIndexStart": 1,
                                "name": self._filter_languages_expr(languages, "$name"),
                            }
                        },
                    ],
                    "as": "book",
                }
            },
            {"$unwind": {"path": "$book", "preserveNullAndEmptyArrays": True}},
            # 🔹 Final projection (reuse your logic)
            {
                "$project": {
                    **self._projection_for_languages(languages),
                    # remove nulls cleanly
                    "edition": {
                        "$cond": [
                            {"$ne": ["$edition", None]},
                            "$edition",
                            "$$REMOVE",
                        ]
                    },
                    "book": {
                        "$cond": [
                            {"$ne": ["$book", None]},
                            "$book",
                            "$$REMOVE",
                        ]
                    },
                }
            },
        ]

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

    def _search_text_projection(
        self, languages: list[str], key: str = "$text"
    ) -> dict[str, Any] | Literal[1]:
        if "*" in languages:
            return 1
        return {language: f"{key}.{language}" for language in languages}

    def _build_search_pipeline(
        self,
        q: str,
        lang: str,
        languages: list[str],
        pagination: PaginationParams,
        edition: PyObjectId | None,
    ) -> list[dict[str, Any]]:
        search_compound: dict[str, Any] = {
            "must": [
                {
                    "text": {
                        "query": q,
                        "path": f"text.{lang}",
                        "fuzzy": {"maxEdits": 1, "prefixLength": 2},
                    }
                }
            ]
        }
        if edition is not None:
            search_compound["filter"] = [
                {
                    "equals": {
                        "path": "editionId",
                        "value": ObjectId(edition),
                    }
                }
            ]

        skip = (pagination.page - 1) * pagination.page_size
        project_stage = {
            "$project": {
                "_id": 1,
                "editionId": 1,
                "bookIndex": 1,
                "hadithIndex": 1,
                "hadithIndexMinor": 1,
                "bookHadithIndex": 1,
                "text": self._search_text_projection(languages),
                "grades": 1,
                "score": {"$meta": "searchScore"},
                "edition": 1,
                "book": 1,
            }
        }

        return [
            {
                "$search": {
                    "index": "hadithSearchIndex",
                    "compound": search_compound,
                }
            },
            {"$limit": 100},
            # 👇 ADD LOOKUPS HERE
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
                                "name": self._filter_languages_expr(languages, "$name"),
                            }
                        },
                    ],
                    "as": "edition",
                }
            },
            {"$unwind": {"path": "$edition", "preserveNullAndEmptyArrays": True}},
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
                                "name": self._filter_languages_expr(languages, "$name"),
                            }
                        },
                    ],
                    "as": "book",
                }
            },
            {"$unwind": {"path": "$book", "preserveNullAndEmptyArrays": True}},
            {
                "$facet": {
                    "items": [
                        project_stage,
                        {"$sort": {"score": -1}},
                        {"$skip": skip},
                        {"$limit": pagination.page_size},
                    ],
                    "total": [{"$count": "count"}],
                }
            },
            {
                "$project": {
                    "items": 1,
                    "total": {"$ifNull": [{"$arrayElemAt": ["$total.count", 0]}, 0]},
                }
            },
        ]

    # ----- GETS -----

    def get_hadith_by_id(
        self, hadith_id: PyObjectId, languages: list[str]
    ) -> dict[str, Any]:
        pipeline = self._build_get_by_id_pipeline(ObjectId(hadith_id), languages)

        hadith = self.repository.find_one_with_lookup(pipeline)

        if hadith is None:
            raise HadithNotFoundError(hadith_id)

        return hadith

    def get_hadiths_paginated(
        self,
        page: int,
        page_size: int,
        filter_query: FilterHadithQueries,
        languages: list[str],
    ) -> dict[str, Any]:
        projection = self._projection_for_languages(languages)
        result = self.repository.paginate(
            page=page,
            page_size=page_size,
            filter_query=filter_query.to_mongo(),
            projection=projection,
            sort=[("hadithIndex", 1), ("hadithIndexMinor", 1)],
        )
        return result

    def get_hadiths_by_edition_paginated(
        self,
        edition_id: PyObjectId,
        page: int,
        page_size: int,
        languages: list[str],
    ) -> dict[str, Any]:
        filter_query = FilterHadithQueries(edition=edition_id)
        return self.get_hadiths_paginated(page, page_size, filter_query, languages)

    def search_hadiths(
        self,
        q: str,
        lang: str,
        languages: list[str],
        pagination: PaginationParams,
        edition: PyObjectId | None,
    ) -> dict[str, Any]:
        pipeline = self._build_search_pipeline(
            q=q,
            lang=lang,
            languages=languages,
            pagination=pagination,
            edition=edition,
        )
        result = self.repository.search(pipeline)
        return {
            "total": result.get("total", 0),
            "page": pagination.page,
            "page_size": pagination.page_size,
            "items": result.get("items", []),
        }

    def get_hadiths_by_edition_and_book_paginated(
        self,
        edition_id: PyObjectId,
        book_index: int,
        page: int,
        page_size: int,
        languages: list[str],
    ) -> dict[str, Any]:
        filter_query = FilterHadithQueries(edition=edition_id, book_index=book_index)
        return self.get_hadiths_paginated(page, page_size, filter_query, languages)

    def get_hadith_by_edition_and_index(
        self, edition_id: PyObjectId, hadith_index: int, languages: list[str]
    ) -> dict[str, Any]:
        projection = self._projection_for_languages(languages)
        filter_query = {
            "editionId": ObjectId(edition_id),
            "hadithIndex": hadith_index,
            "hadithIndexMinor": None,
        }
        hadith = self.repository.find_one(filter_query, projection)
        if hadith is None:
            msg = f"{edition_id}:{hadith_index}"
            raise HadithNotFoundError(msg)

        variants_filter = {
            "editionId": ObjectId(edition_id),
            "hadithIndex": hadith_index,
            "hadithIndexMinor": {"$exists": True, "$ne": None},
        }
        variants = self.repository.find_many(
            variants_filter,
            projection,
            sort=[("hadithIndexMinor", 1)],
        )
        if variants:
            hadith["variants"] = variants
        return hadith

    def get_hadith_variant_by_edition_and_index_minor(
        self,
        edition_id: PyObjectId,
        hadith_index: int,
        hadith_index_minor: int,
        languages: list[str],
    ) -> dict[str, Any]:
        projection = self._projection_for_languages(languages)
        filter_query = {
            "editionId": ObjectId(edition_id),
            "hadithIndex": hadith_index,
            "hadithIndexMinor": hadith_index_minor,
        }
        hadith = self.repository.find_one(filter_query, projection)
        if hadith is None:
            identifier = f"{edition_id}:{hadith_index}.{hadith_index_minor}"
            raise HadithNotFoundError(identifier)
        return hadith

    def get_hadith_by_edition_book_and_index(
        self,
        edition_id: PyObjectId,
        book_index: int,
        book_hadith_index: int,
        languages: list[str],
    ) -> dict[str, Any]:
        projection = self._projection_for_languages(languages)
        filter_query = {
            "editionId": ObjectId(edition_id),
            "bookIndex": book_index,
            "bookHadithIndex": book_hadith_index,
        }
        hadith = self.repository.find_one(filter_query, projection)
        if hadith is None:
            identifier = f"{edition_id}:{book_index}:{book_hadith_index}"
            raise HadithNotFoundError(identifier)
        return hadith

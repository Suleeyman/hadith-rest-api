from typing import Any

from bson import ObjectId

from src.core.language import build_text_projection
from src.core.schema import PyObjectId
from src.modules.hadith.exception import HadithNotFoundError
from src.modules.hadith.repository import HadithRepository
from src.modules.hadith.schema import FilterHadithQueries


class HadithService:
    def __init__(self, repository: HadithRepository):
        self.repository = repository

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
        projection.update(build_text_projection(languages))
        return projection

    def get_hadith_by_id(
        self, hadith_id: PyObjectId, languages: list[str]
    ) -> dict[str, Any]:
        projection = self._projection_for_languages(languages)
        hadith = self.repository.find_one_by_id(ObjectId(hadith_id), projection)
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

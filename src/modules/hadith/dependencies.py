from typing import Annotated

from fastapi import Depends, Path, Query
from pymongo.database import Database

from src.core.language import Carry, Language, resolve_languages
from src.core.schema import PyObjectId
from src.database import get_database
from src.modules.hadith.repository import HadithRepository
from src.modules.hadith.schema import FilterHadithQueries
from src.modules.hadith.service import HadithService

"""
Values
"""
HadithIndex = Annotated[
    int, Path(ge=1, description="Hadith index as it appears in the Edition")
]
HadithIndexMinor = Annotated[
    int, Path(ge=1, description="Hadith variant index (minor)")
]
BookHadithIndex = Annotated[int, Path(ge=1, description="Hadith index within the Book")]

LanguageQuery = Annotated[
    Language,
    Query(
        description="Language code",
        examples=[Language.en, Language.ar_diacritics, Language.bn],
    ),
]


IncludeArabicQuery = Annotated[
    Carry,
    Query(description="Include or exclude arabic (ar) with the selected language"),
]

IncludeArabicDiacriticsQuery = Annotated[
    Carry,
    Query(description="Include or exclude arabic with diacritics (ar-diacritics)"),
]

"""
Objects
"""


def get_hadith_repository(
    db: Annotated[Database, Depends(get_database)],
) -> HadithRepository:
    return HadithRepository(db)


HadithRepositoryDepends = Annotated[HadithRepository, Depends(get_hadith_repository)]


def get_hadith_service(repo: HadithRepositoryDepends) -> HadithService:
    return HadithService(repo)


HadithServiceDepends = Annotated[HadithService, Depends(get_hadith_service)]


def get_language_selection(
    lang: LanguageQuery = Language.en,
    arabic: IncludeArabicQuery = Carry.EXCLUDE,
    arabic_diacritics: IncludeArabicDiacriticsQuery = Carry.EXCLUDE,
) -> list[str]:
    return resolve_languages(
        lang=lang,
        arabic=arabic,
        arabic_diacritics=arabic_diacritics,
    )


LanguageSelectionDepends = Annotated[list[str], Depends(get_language_selection)]


def get_filter_queries(
    edition: Annotated[
        PyObjectId | None,
        Query(description="Edition Id", examples=["69b55e8d6f42ba7ccb2a131d"]),
    ] = None,
    book_index: Annotated[
        int | None, Query(ge=1, description="Book index to filter hadiths")
    ] = None,
) -> FilterHadithQueries:
    return FilterHadithQueries(edition=edition, book_index=book_index)


FilterHadithQueryDepends = Annotated[FilterHadithQueries, Depends(get_filter_queries)]

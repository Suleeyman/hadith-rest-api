from typing import Annotated

from fastapi import Depends, Query
from pydantic import StringConstraints

from src.core.language import Carry, Language, resolve_languages

LanguageQuery = Annotated[
    Language,
    Query(
        description="Language code",
        examples=[Language.en, Language.ar_diacritics, Language.bn],
    ),
]

ManyLanguageQuery = Annotated[
    list[Language],
    Query(
        default_factory=lambda: [Language.en],
        description="Many language code",
        examples=[[Language.en, Language.ar_diacritics, Language.bn]],
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


def get_many_language_selection(
    lang: ManyLanguageQuery,
) -> list[str]:
    # Return as string values, duplicate removed
    return list({lg.value for lg in lang})


ManyLanguageSelectionDepends = Annotated[
    list[str], Depends(get_many_language_selection)
]


SearchQueryDepends = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
    Query(description="Search query"),
]

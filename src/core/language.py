from enum import StrEnum
from typing import Literal


class Carry(StrEnum):
    EXCLUDE = "exclude"
    INCLUDE = "include"


class Language(StrEnum):
    ar = "ar"
    ar_diacritics = "ar-diacritics"
    en = "en"
    fr = "fr"
    tr = "tr"
    ur = "ur"
    id = "id"
    bn = "bn"
    ta = "ta"
    ru = "ru"


class LanguageError(ValueError):
    pass


def resolve_languages(
    lang: Language,
    arabic: Carry = Carry.EXCLUDE,
    arabic_diacritics: Carry = Carry.EXCLUDE,
) -> list[str]:
    lang_value = lang.value

    languages = [lang_value]

    if arabic.value == Carry.INCLUDE and lang_value != Language.ar.value:
        languages.append(Language.ar.value)

    if (
        arabic_diacritics == Carry.INCLUDE
        and lang_value != Language.ar_diacritics.value
    ):
        languages.append(Language.ar_diacritics.value)

    return languages


type MongoProjection = dict[str, Literal[1]]


def build_text_projection(languages: list[str]) -> MongoProjection:
    return {f"text.{language}": 1 for language in languages}


def select_text(
    text: dict[str, str] | None, languages: list[str]
) -> str | dict[str, str]:
    if not text:
        raise LanguageError("Requested language not available.")

    selected = {
        language: text[language]
        for language in languages
        if language in text and text[language] is not None
    }

    if not selected:
        raise LanguageError("Requested language not available.")

    if len(selected) == 1:
        return next(iter(selected.values()))

    return selected

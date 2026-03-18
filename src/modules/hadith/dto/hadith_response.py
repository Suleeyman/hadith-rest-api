from src.modules.hadith.model import Hadith


class HadithWithVariants(Hadith):
    variants: list[Hadith] | None = None

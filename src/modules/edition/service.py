from bson import ObjectId

from src.core.schema import PyObjectId
from src.modules.edition.dto.edition_with_books import EditionWithBooks
from src.modules.edition.exception import EditionNotFoundError
from src.modules.edition.model import Edition
from src.modules.edition.repository import EditionRepository


class EditionService:
    def __init__(self, repository: EditionRepository):
        self.repository = repository

    # ----- BASIC SERVICE -----

    def get_edition_by_id(self, edition_id: PyObjectId) -> Edition:
        edition = self.repository.find_one_by_id(ObjectId(edition_id))
        if edition is None:
            raise EditionNotFoundError(edition_id)
        return Edition(**edition)

    def get_edition_by_slug(self, slug: str) -> Edition:
        edition = self.repository.find_one_by_slug(slug)
        if edition is None:
            raise EditionNotFoundError(slug)
        return Edition(**edition)

    def get_edition_by_identifier(self, identifier: str) -> Edition:
        if ObjectId.is_valid(identifier):
            return self.get_edition_by_id(PyObjectId(identifier))

        return self.get_edition_by_slug(identifier)

    def get_editions(
        self,
    ) -> list[Edition]:
        return list(self.repository.find_all())

    # ----- WITH LOOKUP -----
    def get_edition_by_slug_join_books(self, slug: str) -> EditionWithBooks:
        edition = self.repository.find_one_by_slug_join_books(slug)
        if edition is None:
            raise EditionNotFoundError(slug)
        return EditionWithBooks(**edition)

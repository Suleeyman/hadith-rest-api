from src.exceptions import Resource, ResourceNotFoundError


class EditionNotFoundError(ResourceNotFoundError):
    """Exception raised when a Book resource is not found."""

    def __init__(self, identifier=None, details=None):
        super().__init__(Resource.edition, identifier=identifier, details=details)

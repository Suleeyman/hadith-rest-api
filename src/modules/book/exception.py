from src.exceptions import Resource, ResourceNotFoundError


class BookNotFoundError(ResourceNotFoundError):
    """Exception raised when a Book resource is not found."""

    def __init__(self, identifier=None, details=None):
        super().__init__(Resource.book, identifier=identifier, details=details)

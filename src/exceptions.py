from typing import Any

from src.modules.common.model import Resource


class ResourceNotFoundError(Exception):
    """Base exception for resources that cannot be found."""

    def __init__(
        self, resource_name: Resource, identifier: str | None, details: Any = None
    ):
        self.resource_name = resource_name
        self.identifier = identifier
        self.message = f"{resource_name} not found"
        self.details: Any = details
        if identifier is not None:
            self.details = f"{resource_name} identified by '{identifier}' not found"

        super().__init__()

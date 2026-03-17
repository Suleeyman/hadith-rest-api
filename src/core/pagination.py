from typing import Annotated, Any

from fastapi import Depends, Query
from pymongo.collection import Collection

from src.core.schema import PaginationParams


def get_pagination_params(
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Items per page (max 100)")
    ] = 100,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


PaginationParamsDepends = Annotated[PaginationParams, Depends(get_pagination_params)]


def paginate_collection(
    collection: Collection,
    page: int,
    page_size: int,
    filter_query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size <= 0:
        raise ValueError("page_size must be > 0")

    query = filter_query if filter_query is not None else {}
    skip = (page - 1) * page_size

    total = collection.count_documents(query)
    items = list(collection.find(query).skip(skip).limit(page_size))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }

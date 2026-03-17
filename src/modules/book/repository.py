from typing import Any

from bson import ObjectId
from pymongo.database import Database

from src.core.pagination import paginate_collection

# logging.getLogger("pymongo.command").setLevel(logging.DEBUG)


class BookRepository:
    def __init__(self, database: Database):
        self.collection = database["book"]

    # -------- INTERNAL (DRY) --------

    def _lookup_edition(self):
        return [
            {
                "$lookup": {
                    "from": "edition",
                    "localField": "editionId",
                    "foreignField": "_id",
                    "as": "edition",
                }
            },
            {"$unwind": "$edition"},
        ]

    def _aggregate_one(self, pipeline):
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def _aggregate_many(self, pipeline):
        return list(self.collection.aggregate(pipeline))

    # ----- BASIC FIND -----

    def find_all(self):
        return list(self.collection.find({}))

    def paginate(
        self,
        page: int,
        page_size: int,
        filter_query: dict[str, Any],
    ) -> dict[str, Any]:
        return paginate_collection(
            collection=self.collection,
            page=page,
            page_size=page_size,
            filter_query=filter_query,
        )

    def find_one_by_id(self, document_id: ObjectId):
        return self.collection.find_one({"_id": document_id})

    def find_with_edition_id(self, edition_id: ObjectId):
        return self.collection.find({"editionId": edition_id})

    def find_one_by_book_index_with_edition_id(
        self, book_index: int, edition_id: ObjectId
    ):
        return self.collection.find_one(
            {"editionId": edition_id, "bookIndex": book_index}
        )

    # ----- LOOKUP FIND -----

    def find_all_join_edition(self):
        pipeline = self._lookup_edition()
        return self._aggregate_many(pipeline)

    def find_one_by_id_join_edition(self, document_id: ObjectId):
        pipeline = [{"$match": {"_id": document_id}}, *self._lookup_edition()]
        return self._aggregate_one(pipeline)

    def find_with_edition_id_join_edition(self, edition_id: ObjectId):
        pipeline = [{"$match": {"editionId": edition_id}}, *self._lookup_edition()]
        return self._aggregate_many(pipeline)

    def find_one_by_book_index_with_edition_id_join_edition(
        self, book_index: int, edition_id: ObjectId
    ):
        pipeline = [
            {
                "$match": {
                    "editionId": edition_id,
                    "bookIndex": book_index,
                }
            },
            *self._lookup_edition(),
        ]
        return self._aggregate_one(pipeline)

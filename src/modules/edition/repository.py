from bson import ObjectId
from pymongo.database import Database

# class EditionDoc(TypedDict):
#     _id: ObjectId
#     name: dict[str, str]
#     slug: str
#     hadithCount: int
#     bookCount: int


# class EditionRepository:
#     def __init__(self, database: Database):
#         self.collection: Collection[EditionDoc] = database["edition"]

#     def find_all(self) -> list[Edition]:
#         return list(self.collection.find({}))

#     def find_one_by_id(self, object_id: ObjectId):
#         return self.collection.find_one({"_id": object_id})

#     def find_one_by_slug(self, slug: str) -> Edition | None:
#         return self.collection.find_one({"slug": slug})


class EditionRepository:
    def __init__(self, database: Database):
        self.collection = database["edition"]

    # -------- INTERNAL (DRY) --------

    def _lookup_edition(self):
        return [
            {
                "$lookup": {
                    "from": "book",
                    "localField": "_id",
                    "foreignField": "editionId",
                    "as": "books",
                }
            }
        ]

    def _aggregate_one(self, pipeline):
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def _aggregate_many(self, pipeline):
        return list(self.collection.aggregate(pipeline))

    # ----- BASIC FIND -----

    def find_all(self):
        return list(self.collection.find({}))

    def find_one_by_id(self, document_id: ObjectId):
        return self.collection.find_one({"_id": document_id})

    def find_one_by_slug(self, slug: str):
        return self.collection.find_one({"slug": slug})

    # ----- LOOKUP FIND -----
    def find_one_by_slug_join_books(self, slug: str):
        pipeline = [
            {"$match": {"slug": slug}},
            *self._lookup_edition(),
        ]
        return self._aggregate_one(pipeline)

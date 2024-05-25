from dataclasses import dataclass, field

from bson.objectid import ObjectId
from flask_login import UserMixin

from ..interfaces.mongo_model import MongoModel


@dataclass
class User(UserMixin, MongoModel):
    username: str
    password: str
    id: ObjectId = field(default_factory=ObjectId)

    def to_document(self) -> dict:
        return {"username": self.username, "password": self.password, "_id": self.id}

    @classmethod
    def from_document(cls, doc: dict) -> "User":
        return cls(username=doc["username"], password=doc["password"], id=doc["_id"])

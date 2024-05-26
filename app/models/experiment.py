from dataclasses import InitVar, dataclass, field
from datetime import datetime

from bson import ObjectId

from ..interfaces.mongo_model import MongoModel
from .llm import LLM
from .placeholder import Placeholder
from .role import Role
from .section import Section


@dataclass
class Experiment(MongoModel):
    starting_message: str
    note: str
    favourite: bool
    creator: str

    llms: dict[str, LLM] = field(init=False)
    roles: dict[str, Role] = field(init=False)
    shared_sections: dict[str, Section] = field(init=False)
    summarizer_sections: dict[str, Section] = field(init=False)
    placeholders: dict[str, Placeholder] = field(init=False)

    llms_list: InitVar[list[LLM]]
    roles_list: InitVar[list[Role]]
    shared_sections_list: InitVar[list[Section]]
    summarizer_sections_list: InitVar[list[Section]]
    placeholders_list: InitVar[list[Placeholder]] = field(default=[])

    conversation_ids: list[ObjectId] = field(default_factory=list)
    id: ObjectId = field(default_factory=ObjectId)
    creation_date: datetime = field(default_factory=datetime.now)

    def __post_init__(
        self,
        llms_list: list[LLM],
        roles_list: list[Role],
        shared_sections_list: list[Section],
        summarizer_sections_list: list[Section],
        placeholders_list: list[Placeholder],
    ) -> None:
        self.llms = {llm.name: llm for llm in llms_list}
        self.roles = {role.name: role for role in roles_list}
        self.shared_sections = {
            section.title: section for section in shared_sections_list
        }
        self.summarizer_sections = {
            section.title: section for section in summarizer_sections_list
        }
        if not placeholders_list:
            placeholders_list = self._create_starting_placeholders()
        self.placeholders = {
            placeholder.tag: placeholder for placeholder in placeholders_list
        }

    def _create_starting_placeholders(self) -> list[Placeholder]:
        return [
            Placeholder(tag=f"<AGENTS_NUM>"),
            Placeholder(tag=f"<ROLES_NUM>"),
        ]

    @classmethod
    def from_document(cls, doc: dict) -> "Experiment":
        return cls(
            starting_message=doc["starting_message"],
            llms_list=[LLM.from_document(llm) for llm in doc["llms"]],
            roles_list=[Role.from_document(role) for role in doc["roles"]],
            shared_sections_list=[
                Section.from_document(section) for section in doc["shared_sections"]
            ],
            summarizer_sections_list=[
                Section.from_document(section) for section in doc["summarizer_sections"]
            ],
            placeholders_list=[
                Placeholder.from_document(placeholder)
                for placeholder in doc["placeholders"]
            ],
            note=doc["note"],
            favourite=doc["favourite"],
            creator=doc["creator"],
            conversation_ids=doc["conversation_ids"],
            id=doc["_id"],
            creation_date=doc["creation_date"],
        )

    def to_document(self) -> dict:
        return {
            "_id": self.id,
            "starting_message": self.starting_message,
            "llms": [llm.to_document() for llm in self.llms.values()],
            "roles": [role.to_document() for role in self.roles.values()],
            "shared_sections": [
                section.to_document() for section in self.shared_sections.values()
            ],
            "summarizer_sections": [
                section.to_document() for section in self.summarizer_sections.values()
            ],
            "placeholders": [
                placeholder.to_document() for placeholder in self.placeholders.values()
            ],
            "note": self.note,
            "favourite": self.favourite,
            "creator": self.creator,
            "conversation_ids": self.conversation_ids,
            "creation_date": self.creation_date,
        }

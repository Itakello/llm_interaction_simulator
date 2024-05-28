from dataclasses import InitVar, dataclass, field

from itakello_logging import ItakelloLogging

from ..interfaces.mongo_model import MongoModel
from .placeholder import Placeholder
from .section import Section

logger = ItakelloLogging().get_logger(__name__)


@dataclass
class Role(MongoModel):
    name: str

    sections_list: InitVar[list[Section]]
    placeholders_list: InitVar[list[Placeholder]] = field(default=[])

    sections: dict[str, Section] = field(init=False)
    placeholders: dict[str, Placeholder] = field(init=False)

    def __post_init__(
        self, sections_list: list[Section], placeholders_list: list[Placeholder]
    ) -> None:
        if not placeholders_list:
            placeholders_list = self._create_starting_placeholders()

        self.placeholders = {
            placeholder.tag: placeholder for placeholder in placeholders_list
        }
        self.sections = {section.title: section for section in sections_list}

        logger.debug(
            f"Created new role [{self.name}] with:\n"
            + f"- {len(self.sections)} private sections\n"
            + f"- {len(self.placeholders)} placeholders"
        )

    def __str__(self) -> str:
        sections = "\n".join([str(section) for section in self.sections.values()])
        placeholders = "\n- ".join(
            [str(placeholder) for placeholder in self.placeholders.values()]
        )
        return (
            "----------------------------------------\n"
            + f"\033[1mName\033[0m: {self.name}\n\n"
            + f"\033[1mPrivate sections\033[0m:\n-----\n{sections}-----\n\n"
            + f"\033[1mPlaceholders\033[0m:\n- {placeholders}\n"
            + "----------------------------------------"
        )

    @classmethod
    def from_document(cls, doc: dict) -> "Role":
        return cls(
            name=doc["name"],
            sections_list=[
                Section.from_document(section) for section in doc["sections"]
            ],
            placeholders_list=[
                Placeholder.from_document(placeholder)
                for placeholder in doc["placeholders"]
            ],
        )

    def to_document(self) -> dict:
        return {
            "name": self.name,
            "sections": [section.to_document() for section in self.sections.values()],
            "placeholders": [
                placeholder.to_document() for placeholder in self.placeholders.values()
            ],
        }

    def print_placeholders(self) -> None:
        placeholders = "\n".join(
            [str(placeholder) for placeholder in self.placeholders.values()]
        )
        logger.info(
            f"Available placeholders for {self.name.upper()} agent:\n{placeholders}\n"
        )

    def _create_starting_placeholders(self) -> list[Placeholder]:
        return [
            Placeholder(tag=f"<{self.name.upper()}_NOUN>"),
            Placeholder(tag=f"<{self.name.upper()}_POSS>"),
            Placeholder(tag=f"<{self.name.upper()}_NUM>"),
        ]

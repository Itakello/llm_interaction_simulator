from dataclasses import dataclass
from typing import Any, Literal

from itakello_logging import ItakelloLogging

from ...abstracts import BaseManager
from ...core.input_manager import InputManager
from ...utility.consts import DEV_MODE
from ...utility.custom_os import CustomOS
from ...utility.enums import SectionType
from ..placeholder.placeholder import Placeholder
from ..role.role import Role
from .section import Section

logger = ItakelloLogging().get_logger(__name__)


@dataclass
class SectionManager(BaseManager):
    input_m: InputManager

    def ask_for_updated_sections(
        self,
        old_sections: dict[str, Section],
        type: Literal[SectionType.SUMMARIZER, SectionType.ROLES],
    ) -> list[Section]:
        instructions = (
            "1. The new sections will be appended to the existing one, using the new order\n"
            + "2. The sections that are not reinserted will be deleted.\n"
        )
        if type == SectionType.ROLES:
            instructions += "3. If a section changes from shared to private (or viceversa), you will be asked to insert the new content\n"
        logger.instruction(instructions)

        old_sections_titles = [
            (
                section.title
                if section.type == SectionType.PRIVATE
                or section.type == SectionType.SUMMARIZER
                else f"{section.title} (SHARED)"
            )
            for section in old_sections.values()
        ]
        logger.info("Previous sections: " + ", ".join(old_sections_titles[1:]))

        new_sections = self.ask_for_sections(type=type)
        return new_sections

    def ask_for_sections(
        self, type: Literal[SectionType.SUMMARIZER, SectionType.ROLES]
    ) -> list[Section]:
        logger.instruction(
            "1. The sections will be ordered by the order you insert them\n"
            + "2. A 'Starting prompt' section without title will be dynamically added to the prompt\n"
            + f"3. The inserted sections will be used only for the {type.value}\n"
        )
        if CustomOS.getenv("APP_MODE", "") == DEV_MODE:
            if type == SectionType.ROLES:
                sections_titles = CustomOS.getenv("AGENTS_SECTIONS").split(",")
            else:
                sections_titles = CustomOS.getenv("SUMMARIZER_SECTIONS").split(",")
        else:
            sections_titles = self.input_m.input_list(
                f"Enter the {type.value.upper()} section titles:",
                example="goal, personality, communication_rules, ...",
            )
        sections_titles.insert(0, "starting_prompt")
        sections = [
            Section(index=i, title=title, content="", type=type)
            for i, title in enumerate(sections_titles)
        ]
        return sections

    def ask_shared_sections(
        self, sections: list[Section]
    ) -> tuple[list[Section], list[Section]]:
        assert all(
            section.type == SectionType.ROLES for section in sections
        ), logger.critical("Not all sections are of type AGENTS")

        if CustomOS.getenv("APP_MODE", "") == DEV_MODE:
            shared_section_titles = CustomOS.getenv("SHARED_SECTIONS").split(",")
        else:
            choices = [section.title for section in sorted(sections)]
            shared_section_titles = self.input_m.select_multiple(
                message="Select shared sections between the agents",
                choices=choices,
            )

        shared_sections = []
        private_sections = []
        for section in sections:
            if section.title in shared_section_titles:
                section.type = SectionType.SHARED
                shared_sections.append(section)
            else:
                section.type = SectionType.PRIVATE
                private_sections.append(section)
        return shared_sections, private_sections

    def ask_content(self, section: Section) -> set[str]:
        message = f"Enter the content for the [{section.type.value}] [{section.title}] section"
        if section.type == SectionType.PRIVATE:
            assert section.role, logger.error("Private section without role")
            message += f" of [{section.role.capitalize()}] agents"
        if CustomOS.getenv("APP_MODE", "") == DEV_MODE:
            content = CustomOS.getenv("AGENTS_CONTENT")
        else:
            content = self.input_m.input_str(message)
        new_placeholders = section.set_content(content)
        return new_placeholders

    def get_agent_combinations(
        self, role_agents_num: list[tuple[str, int]], try_each_combination: bool
    ) -> list[list[tuple[str, int]]]:
        agent_combinations = []
        if try_each_combination:
            self.generate_combinations(role_agents_num, [], 0, agent_combinations)
        else:
            agent_combinations.append(role_agents_num)
        return agent_combinations

    def generate_combinations(
        self,
        nums: list[Any],
        current_combination: list[Any],
        index: int,
        result: list[list[tuple[str, int]]],
    ) -> None:
        if index == len(nums):
            result.append(current_combination.copy())
            return
        for i in range(1, nums[index][1] + 1):
            current_combination.append((nums[index][0], i))
            self.generate_combinations(nums, current_combination, index + 1, result)
            current_combination.pop()

    def list_combinations(
        self, nums: list[tuple[str, int]]
    ) -> list[list[tuple[str, int]]]:
        result = []
        self.generate_combinations(nums, [], 0, result)
        return result

    def compose_placeholders(
        self, agent_combination: list[tuple[str, int]]
    ) -> dict[str, str]:
        placeholders = {}
        total_agents = 0
        for role, num in agent_combination:
            total_agents += num
            for placeholder in self.roles[role].placeholders.values():
                placeholders[placeholder.tag] = placeholder.to_value(num)
        for placeholder in self.placeholders.values():
            if placeholder.role == "roles":
                placeholders[placeholder.tag] = placeholder.to_value(
                    len(agent_combination)
                )

            elif placeholder.role == "agents":
                placeholders[placeholder.tag] = placeholder.to_value(total_agents)
            else:
                logger.error(f"Invalid placeholder role: {placeholder.role}")
                exit()
        return placeholders

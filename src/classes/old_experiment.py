import datetime
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import cast

import autogen
from bson.objectid import ObjectId

from ..agents import Agent, Guard, Manager, Prisoner, Researcher, Summarizer
from ..handlers.config_handler import ConfigHandler
from ..handlers.db_handler import DBHandler
from ..serializers import DocumentSerializer
from .chat import Chat
from .conversation import Conversation

logger = logging.getLogger(__name__)


@dataclass
class OldExperiment(DocumentSerializer):
    description: str
    id: ObjectId = field(init=False)
    creation_date: datetime = field(default=datetime.now())
    # conversations: list[] = field(init=False)
    config: dict = field(init=False)
    researcher: Researcher = field(init=False)
    agents: list[Agent] = field(init=False)
    group_chat: Chat = field(init=False)
    manager: Manager = field(init=False)
    summarizer: Summarizer = field(init=False)

    def __post_init__(self) -> None:
        self.config = ConfigHandler().get_section(name="Experiment")
        llm_config = self._get_config_llm()
        self.researcher = Researcher()
        self.agents = self._get_agents(llm_config)
        self.summarizer = Summarizer(
            llm_config=llm_config,
            n_guards=int(self.config["n_guards"]),
            n_prisoners=int(self.config["n_prisoners"]),
        )
        self.group_chat = Chat(
            agents=cast(list[autogen.Agent], self.agents),
            selection_method=self.config["manager_selection_method"],
            round_number=int(self.config["conversation_rounds"]),
        )
        self.manager = Manager(groupchat=self.group_chat, llm_config=llm_config)
        logger.info(
            f"Experiment created with config:\n{json.dumps(self.config, indent=2)}"
        )
        # self.id = self.db_handler.save_experiment(doc=self.to_document())

    def to_document(self) -> dict:
        doc = self.config.copy()
        return doc

    def perform(self) -> Conversation:
        start_message = self.config["researcher_initial_message"]
        conversation = Conversation()
        for i in range(int(self.config["experiment_days"])):
            self.researcher.initiate_chat(
                recipient=self.manager, clear_history=True, message=start_message
            )
            raw_conversation = self.group_chat.messages[1:]
            summary = self.summarizer.generate_summary(
                previous_conversation=raw_conversation, round_number=i + 1
            )
            conversation.add_daily_conversation(raw_conversation, day=i + 1)
            start_message += "\n" + summary
        logger.info("Experiment complete")
        return conversation

    def _get_config_llm(self) -> dict:
        model = self.config["llm"]
        config_list = autogen.config_list_from_json(
            env_or_file="config/OAI_CONFIG_LIST", filter_dict={"model": [model]}
        )
        llm_config = {
            "config_list": config_list,
            "cache_seed": None,  # set to None to disable caching and have a new conversation every time
        }
        logger.debug(f"LLM config: {json.dumps(llm_config, indent=2)}")
        return llm_config

    def _get_agents(
        self,
        llm_config: dict,
    ) -> list[Agent]:
        agents = []
        n_guards = int(self.config["n_guards"])
        n_prisoners = int(self.config["n_prisoners"])
        agents_fields = [w.strip() for w in self.config["agents_fields"].split(",")]
        for _ in range(n_guards):
            agents.append(
                Guard(
                    llm_config=llm_config,
                    n_guards=n_guards,
                    n_prisoners=n_prisoners,
                    agent_fields=agents_fields,
                )
            )
        for _ in range(n_prisoners):
            agents.append(
                Prisoner(
                    llm_config=llm_config,
                    n_guards=n_guards,
                    n_prisoners=n_prisoners,
                    agent_fields=agents_fields,
                )
            )
        logger.info(f"Created {n_guards} Guards and {n_prisoners} Prisoners")
        return agents

    def load_from_db(self):
        pass

    def fetch_conversations(self):
        pass

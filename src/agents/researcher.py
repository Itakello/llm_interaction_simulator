import logging
from dataclasses import dataclass

from autogen import UserProxyAgent

logger = logging.getLogger(__name__)


@dataclass
class Researcher(UserProxyAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Researcher", human_input_mode="NEVER", code_execution_config=False
        )
        logger.debug("Researcher created")

    def __hash__(self) -> int:
        return super().__hash__()

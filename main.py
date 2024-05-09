from dotenv import load_dotenv
from itakello_logging import ItakelloLogging

from src.llm_simulator.components.conversation.conversation_manager import (
    ConversationManager,
)
from src.llm_simulator.components.experiment.experiment_manager import ExperimentManager
from src.llm_simulator.core.action_manager import ActionManager
from src.llm_simulator.core.database_manager import DatabaseManager
from src.llm_simulator.core.input_manager import InputManager
from src.llm_simulator.utility.custom_os import CustomOS

logger = ItakelloLogging.get_logger(__name__)


def main() -> None:
    logger.debug("[Test debug mode]")
    input_m = InputManager()
    db_m = DatabaseManager(input_m=input_m)
    action_m = ActionManager(input_m=input_m)

    experiment_m = ExperimentManager(input_m=input_m, db_m=db_m)
    conversation_m = ConversationManager(input_m=input_m, db_m=db_m)

    while True:
        action = action_m.select_initial_action()
        if action == "Create new experiment":  # ✅
            experiment = experiment_m.create_experiment(creator=db_m.username)
        elif action == "Select experiment":  # ✅
            experiment = experiment_m.select_experiment()
            if experiment == None:
                logger.warning("No experiments available. Please create a new one.")
                continue
        else:  # Exit the application
            break
        logger.info(f"\nSelected experiment:\n\n{experiment.to_contents()}")
        while True:
            action = action_m.select_experiment_action()
            if action == "Perform new conversations":  # ✅
                conversation_m.perform_conversations(experiment)
                continue
            elif action == "Duplicate and update experiment":  # ✅
                experiment_m.duplicate_and_update_experiment(experiment)
                if experiment != None:
                    logger.info(
                        f"\nDuplicated and updated experiment:\n\n{experiment.to_contents()}"
                    )
                break
            elif action == "Update experiment (Favourites and Notes)":  # ✅
                if experiment.creator != db_m.username:
                    logger.warning(
                        "You are not the creator of this experiment. You cannot modify it."
                    )
                    continue
                experiment_m.update_experiment(experiment)
                continue
            elif action == "Select old conversations":  # ✅
                conversation = conversation_m.select_conversation(experiment)
                if conversation == None:
                    logger.warning(
                        "No conversations available for this experiment. Please perform new ones."
                    )
                    continue
            elif action == "Delete experiment":  # ✅
                if experiment.creator != db_m.username:
                    logger.warning(
                        "You are not the creator of this experiment. You cannot delete it."
                    )
                    continue
                if input_m.confirm("Are you sure you want to delete this experiment?"):
                    experiment_m.delete_experiment(experiment)
                    break
                continue
            else:  # Go back
                break
            logger.info(f"\nSelected conversation:\n\n{conversation.to_content()}")
            while True:
                action = action_m.select_conversation_action()
                if action == "View conversation":  # ✅
                    conversation_m.view_conversation(conversation)
                    pass
                elif action == "Set as favourite":  # ✅
                    if experiment.creator != db_m.username:
                        logger.warning(
                            "You are not the creator of this conversastion. You cannot modify it."
                        )
                        continue
                    conversation_m.toggle_favourite(conversation)
                    continue
                elif action == "Delete conversation":  # ✅
                    if conversation.creator != db_m.username:
                        logger.warning(
                            "You are not the creator of this conversation. You cannot delete it."
                        )
                        continue
                    if input_m.confirm(
                        "Are you sure you want to delete this conversation?"
                    ):
                        conversation_m.delete_conversation(experiment, conversation)
                        break
                else:  # Go back
                    break


if __name__ == "__main__":
    load_dotenv()
    ItakelloLogging(
        debug=False,
        excluded_modules=[
            "docker.utils.config",
            "docker.auth",
            "httpx",
            "httpcore.connection",
            "httpcore.http11",
            "autogen.io.base",
            "asyncio",
            "openai._base_client",  # Remove to see API requests debug logs
        ],
    )
    main()

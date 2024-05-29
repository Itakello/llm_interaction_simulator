import os
from dataclasses import dataclass, field

from bson.objectid import ObjectId
from itakello_logging import ItakelloLogging
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import (
    ConfigurationError,
    OperationFailure,
    ServerSelectionTimeoutError,
)
from pymongo.server_api import ServerApi

from ..interfaces.base_manager import BaseManager
from ..models.conversation import Conversation
from ..models.experiment import Experiment
from ..models.user import User

logger = ItakelloLogging().get_logger(__name__)


@dataclass
class DatabaseManager(BaseManager):
    username: str = field(init=False)
    password: str = field(init=False)
    cluster_url: str = field(init=False)
    client: MongoClient = field(init=False)
    db: Database = field(init=False)

    def __post_init__(self) -> None:
        self.username = os.getenv("DB_USER", "default_user")
        self.password = os.getenv("DB_PASSWORD", "default_password")
        self.cluster_url = os.getenv("DB_CLUSTER_URL", "default_cluster_url")
        self.client = self._connect_to_database()
        self.db = self._select_database(self.client)
        super().__post_init__()

    def _connect_to_database(self) -> MongoClient:
        try:
            client = MongoClient(
                f"mongodb+srv://{self.username}:{self.password}@{self.cluster_url}/",
                server_api=ServerApi("1"),
            )
            self._check_connection(client)
            return client
        except Exception as e:
            raise ValueError(f"Failed to create MongoDB client: {e}")

    def _check_connection(self, client: MongoClient) -> None:
        try:
            client.admin.command("ping")
            print("MongoDB connection established.")
        except ConfigurationError:
            raise ValueError("Invalid cluster URL")
        except OperationFailure:
            raise ValueError("Authentication failed")
        except ServerSelectionTimeoutError:
            raise ValueError(
                "Connection timeout. Ask the DB administrator to add your IP to the whitelist"
            )
        except Exception as e:
            raise ValueError(f"Connection error: {e}")

    def _select_database(self, client: MongoClient) -> Database:
        selected_db = os.getenv("DB_NAME", "default_db")
        logger.debug(f"Selected database: {selected_db}")
        return client[selected_db]

    # --------------------- Users ---------------------

    def get_user_by_username(self, username: str) -> User | None:
        user_data = self.db.users.find_one({"username": username})
        if user_data:
            return User.from_document(user_data)
        return None

    def get_user_by_id(self, user_id: str) -> User | None:
        user_data = self.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User.from_document(user_data)
        return None

    def insert_user(self, user: User) -> None:
        self.db.users.insert_one(user.to_document())
        logger.debug(f"User inserted: {user}")

    # --------------------- Experiments ---------------------

    def get_experiments(self) -> dict[str, Experiment]:
        experiment_docs = list(self.db.experiments.find())
        experiments = {
            str(doc["_id"]): Experiment.from_document(doc) for doc in experiment_docs
        }
        logger.debug(f"Experiments retrieved: {len(experiments)}")
        return experiments

    def get_experiment(self, experiment_id: str) -> Experiment:
        experiment_data = self.db.experiments.find_one({"_id": ObjectId(experiment_id)})
        if not experiment_data:
            raise ValueError(f"Experiment with ID {experiment_id} not found")
        experiment = Experiment.from_document(experiment_data)
        logger.debug(f"Experiment retrieved with ID: {experiment_id}")
        return experiment

    def save_experiment(self, experiment: Experiment) -> None:
        self.db.experiments.insert_one(experiment.to_document())
        logger.debug(f"Experiment saved with ID: {experiment.id}")

    def update_experiment(self, experiment: Experiment) -> None:
        self.db.experiments.update_one(
            {"_id": experiment.id},
            {"$set": experiment.to_document()},
        )
        logger.debug(f"Experiment updated with ID: {experiment.id}")

    # --------------------- Conversations ---------------------

    def get_conversations(
        self, conversation_ids: list[ObjectId]
    ) -> dict[str, Conversation]:
        # Retrieve the conversations from the database
        conversation_docs = list(
            self.db.conversations.find({"_id": {"$in": conversation_ids}})
        )
        conversations = {
            str(doc["_id"]): Conversation.from_document(doc)
            for doc in conversation_docs
        }
        logger.debug(f"Conversations retrieved: {len(conversation_docs)}")
        return conversations

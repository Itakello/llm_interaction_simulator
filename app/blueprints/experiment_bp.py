import json

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required
from werkzeug import Response

from ..managers.database_manager import DatabaseManager
from ..models.experiment import Experiment
from ..models.llm import LLM
from ..models.role import Role
from ..models.section import Section
from ..utility.enums import SectionType

experiment_bp = Blueprint("experiment_bp", __name__)


@experiment_bp.route("/", methods=["GET"])
@login_required
def index() -> str:
    db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
    experiments = db_manager.get_experiments()
    return render_template("index.html", experiments=experiments)


@experiment_bp.route("/experiment/create", methods=["GET", "POST"])
@login_required
def create_experiment() -> Response | str:
    db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
    if request.method == "POST":

        data = json.loads(request.form["serialized_data"])

        # TODO parse sections and roles
        roles = [
            Role(
                name=role["name"],
                sections_list=[
                    Section(type=SectionType("Private"), **section)
                    for section in role["sections"]
                ],
            )
            for role in data["roles"]
        ]
        llms = [LLM(model=llm) for llm in data["llms"]]
        shared_sections = [
            Section(type=SectionType("Shared"), **section)
            for section in data["sections"]
        ]

        experiment = Experiment(
            starting_message=data["starting_message"],
            note=data["note"],
            favourite=data["favourite"],
            creator=data["creator"],
            llms_list=llms,
            roles_list=roles,
            shared_sections_list=shared_sections,
        )

        db_manager.save_experiment(experiment)
        return redirect(url_for("experiment_bp.index"))

    context = {
        "creator": db_manager.username,
        "starting_message": "Initiate the experiment",
        "llms": [
            {"value": "llm1", "label": "LLM 1", "selected": False},
            {"value": "llm2", "label": "LLM 2", "selected": False},
            {"value": "llm3", "label": "LLM 3", "selected": False},
        ],
    }

    return render_template("create_experiment.html", **context)


"""@experiment_bp.route("/experiment/<str:id_experiment>", methods=["GET", "POST"])
@login_required
def experiment_detail(id_experiment: str) -> str:
    db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
    experiment = db_manager.get_experiment(id_experiment)
    if request.method == "POST":
        # Handle form submission for updating metadata
        experiment.note = request.form["note"]
        experiment.favourite = "favourite" in request.form
        db_manager.update_experiment(experiment)
        flash("Experiment updated successfully!", "success")
    conversations = db_manager.get_conversations(id_experiment)
    return render_template("experiment_detail.html", experiment=experiment)"""

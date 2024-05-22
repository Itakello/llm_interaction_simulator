from flask import current_app, redirect, render_template, request, url_for


def initialize_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/submit", methods=["POST"])
    def submit():
        data = request.form["data"]
        db = current_app.db
        db.collection_name.insert_one(
            {"data": data}
        )  # Replace 'collection_name' with your actual collection name
        return redirect(url_for("index"))

# -*- coding: utf-8 -*-
import json
from flask import Blueprint, render_template, redirect, request
from app.models import db, User, Sprint, Story, Task
from flask_login import login_user, logout_user, current_user

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route("/")
def index():
    return render_template("index.html")


@main_blueprint.route("/login")
def login():
    next_url = request.args.get("next", "")
    if current_user.is_authenticated:
        return redirect("/")
    return render_template("login.html", users=User.query.all(), next=next_url)


@main_blueprint.route("/login/<user_id>")
def user_login(user_id):
    user = User.query.get(user_id)
    next_url = request.args.get("next", "/")

    if not user:
        return redirect("/login")

    login_user(user)
    return redirect(next_url)


@main_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@main_blueprint.route("/sprints")
def all_sprints():
    sprints = Sprint.query.all()

    return render_template("sprints.html", sprints=sprints)


@main_blueprint.route("/sprints/<sprint_id>", methods=["GET", "POST"])
def view_sprint(sprint_id):
    sprint = Sprint.query.get_or_404(sprint_id)

    if request.method == "GET":
        return render_template("sprint.html", sprint=sprint, users=User.query.all())

    db.session.autoflush = False
    try:
        sprint.start = request.form["start"]
        sprint.ende = request.form["ende"]

        for story_data in json.loads(request.form["data"]):
            story = Story.query.get(story_data["id"])
            if not story:
                story = Story()
                story.sprint = sprint
                db.session.add(story)

            Task.query.filter_by(story_id=story.id).delete()
            for task_data in story_data["tasks"]:
                task = Task()

                task.story = story
                task.status = task_data["status"]
                task.name = task_data["name"]
                task.user = User.query.get(task_data["user_id"])

                story.tasks.append(task)
                db.session.add(task)

        db.session.commit()

        return redirect(f"/sprints/{sprint_id}")
    except KeyError as e:
        raise e
        return "Error"

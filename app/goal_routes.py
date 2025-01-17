from app import db
from flask import Blueprint, jsonify, abort, make_response, request
from app.models.goal import Goal
from app.models.task import Task
import datetime
import requests
import os

goal_bp = Blueprint("goals", __name__, url_prefix="/goals")


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response(
            jsonify({"message": f"{cls.__name__} {model_id} invalid"}), 400))

    model = cls.query.get(model_id)
    if not model:
        abort(make_response(
            jsonify({"message": f"{cls.__name__} {model_id} not found"}), 404))

    return model


@goal_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    try:
        request_body["title"]
    except:
        abort(make_response(jsonify({"details": "Invalid data"}), 400))

    new_goal = Goal.from_dict(request_body)

    db.session.add(new_goal)
    db.session.commit()

    response_body = {"goal": new_goal.to_dict()}

    return make_response(jsonify(response_body), 201)


@goal_bp.route("", methods=["GET"])
def get_goals():
    goals = Goal.query.all()
    results = [goal.to_dict() for goal in goals]

    return jsonify(results)


@goal_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    response_body = {"goal": goal.to_dict()}

    return response_body


@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    goal_updates = request.get_json()
    goal.title = goal_updates["title"]
    response_body = {"goal": goal.to_dict()}
    db.session.commit()

    return response_body


@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal_to_delete = validate_model(Goal, goal_id)
    db.session.delete(goal_to_delete)
    db.session.commit()
    response_body = {
        "details": f'Goal {goal_to_delete.goal_id} "{goal_to_delete.title}" successfully deleted'}

    return make_response(jsonify(response_body))


@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_task_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    for task_id in request_body["task_ids"]:
        task = validate_model(Task, task_id)
        task.goal_id = goal.goal_id
    db.session.commit()
    task_id_list = []
    for task in goal.tasks:
        task_id_list.append(task.task_id)

    response_body = {
        "id": goal.goal_id,
        "task_ids": task_id_list
    }
    return make_response(jsonify(response_body))


@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_of_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    response_body = goal.to_dict(tasks=True)

    return make_response(jsonify(response_body))

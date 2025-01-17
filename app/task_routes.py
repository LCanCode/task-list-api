from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, abort, make_response, request
import datetime, requests, os

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response(jsonify({"message":f"{cls.__name__} {model_id} invalid"}), 400))
    
    model = cls.query.get(model_id)
    if not model:
        abort(make_response(jsonify({"message":f"{cls.__name__} {model_id} not found"}), 404))

    return model


@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    try:
        request_body["title"] and request_body["description"]
    except:
        abort(make_response(jsonify({"details":"Invalid data"}), 400))

    new_task = Task.from_dict(request_body)
    
    db.session.add(new_task)
    db.session.commit()

    response_body = {"task":new_task.to_dict()}

    return make_response(jsonify(response_body), 201)


@task_bp.route("", methods=["GET"])
def get_task():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title).all()
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc()).all()

    else:
        tasks = Task.query.all()
    results = [task.to_dict() for task in tasks]

    return jsonify(results)


@task_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    response_body = {"task":task.to_dict()}

    return response_body


@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = validate_model(Task, task_id)
    task_updates = request.get_json()
    task.title = task_updates["title"]
    task.description = task_updates["description"]
    response_body = {"task":task.to_dict()}
    db.session.commit()

    return response_body

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task_to_delete = validate_model(Task, task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    response_body = {"details": f'Task {task_to_delete.task_id} "{task_to_delete.title}" successfully deleted'}
    

    return make_response(jsonify(response_body)) 

@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.datetime.now()
    
    response_body = {"task": task.to_dict()}
    db.session.commit()
    
    path = "https://slack.com/api/chat.postMessage"
    api_key = os.environ.get("SLACKBOT_API_TOKEN")
    headers = {
        "authorization": f"Bearer {api_key}"
    }

    data = {
        "channel": "C0572HAGWUX",
        "text": f"Someone just completed the task {task.title}"
    }
    requests.post(path, headers=headers, data=data)
    
    return response_body

@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    
    response_body = {"task": task.to_dict()}
    db.session.commit()

    return response_body

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import text
from app.extensions import db
from app.models import CallLog

history_bp = Blueprint("history", __name__)


@history_bp.route("/api/health", methods=["GET"])
def health():
    status = {"redis": "ok", "postgres": "ok"}
    http_status = 200

    try:
        rc = current_app.extensions["redis_client"]
        rc.ping()
    except Exception as e:
        status["redis"] = str(e)
        http_status = 500

    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        status["postgres"] = str(e)
        http_status = 500

    return jsonify(status), http_status


@history_bp.route("/call-history", methods=["GET"])
def call_history():
    limit = request.args.get("limit", 20, type=int)
    from_number = request.args.get("from_number")
    selection = request.args.get("selection")

    query = CallLog.query

    if from_number:
        query = query.filter(CallLog.from_number == from_number)
    if selection:
        query = query.filter(CallLog.menu_selection == selection)

    logs = query.order_by(CallLog.created_at.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs])

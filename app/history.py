from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import text
from app.extensions import db
from app.models import CallLog

history_bp = Blueprint("history", __name__)


@history_bp.route("/api/debug", methods=["GET"])
def debug():
    from sqlalchemy import inspect
    info = {}
    try:
        uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        info["db_host"] = uri.split("@")[-1].split("/")[0] if "@" in uri else "(none)"
        info["tables"] = inspect(db.engine).get_table_names()
        info["models"] = list(db.metadata.tables.keys())
    except Exception as e:
        info["inspect_error"] = f"{type(e).__name__}: {e}"
    try:
        CallLog.query.limit(1).all()
        info["query_call_logs"] = "ok"
    except Exception as e:
        info["query_call_logs"] = f"{type(e).__name__}: {e}"
    return jsonify(info)


@history_bp.route("/api/setup-db", methods=["GET", "POST"])
def setup_db():
    # Flask-Migrate can't run on serverless — create the tables on demand.
    # Hit this once after deploy (or whenever the schema is missing).
    try:
        db.create_all()
        return jsonify({"status": "ok", "message": "tables created"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@history_bp.route("/api/health", methods=["GET"])
def health():
    result = {"redis": "ok", "postgres": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
    http_status = 200

    try:
        rc = current_app.extensions["redis_client"]
        rc.ping()
    except Exception as e:
        result["redis"] = str(e)
        http_status = 500

    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        result["postgres"] = str(e)
        http_status = 500

    result["status"] = "healthy" if http_status == 200 else "unhealthy"
    return jsonify(result), http_status


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

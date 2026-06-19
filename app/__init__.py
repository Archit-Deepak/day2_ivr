import redis
from flask import Flask
from flask_migrate import Migrate

from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    rc = redis.from_url(app.config["REDIS_URL"])
    app.extensions["redis_client"] = rc

    from app.ivr import ivr_bp
    from app.history import history_bp

    app.register_blueprint(ivr_bp)
    app.register_blueprint(history_bp)

    # Import models so Flask-Migrate can detect them
    from app import models  # noqa: F401

    return app

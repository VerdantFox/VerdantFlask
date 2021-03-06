import os
from datetime import datetime

from bson import ObjectId, json_util
from dotenv import load_dotenv
from flask import Flask
from flask.json import JSONEncoder

from src.globals import db, login_manager
from src.routes.blog.views import blog
from src.routes.core.views import core
from src.routes.error_pages.handlers import error_pages
from src.routes.finance.views import finance
from src.routes.users.views import users


class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def register_blueprints(app: Flask) -> None:
    """Register app blueprints with url prefix locations"""
    app.register_blueprint(core, url_prefix="")
    app.register_blueprint(users, url_prefix="/users")
    app.register_blueprint(blog, url_prefix="/blog")
    app.register_blueprint(finance, url_prefix="/finance")
    app.register_blueprint(error_pages, url_prefix="/error")


def set_app_config(app: Flask) -> None:
    """Set app config items from environment variables"""
    # Flask stuff
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # DB stuff
    app.config["MONGODB_SETTINGS"] = {
        "authentication_source": "admin",
        "host": os.getenv("MONGODB_HOST"),
        "port": int(os.getenv("MONGODB_PORT", "5000")),
        "username": os.getenv("MONGODB_USERNAME"),
        "password": os.getenv("MONGODB_PASSWORD"),
    }
    # Adjust mongodb settings for pytest
    if os.getenv("PYTEST", "").lower() in ("1", "true"):
        app.config["MONGODB_SETTINGS"] = {
            "host": "mongodb://admin:admin@localhost:27017/flask?authSource=admin",
        }


def create_app() -> Flask:
    """Create the Flask app and set its configuration"""

    load_dotenv()

    # Initiate app
    app = Flask(__name__)
    app.json_encoder = MongoJsonEncoder

    # Update config from environment variables
    set_app_config(app)

    # register blueprints
    register_blueprints(app)

    # initialize databases
    db.init_app(app)

    # initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "users.login"

    return app

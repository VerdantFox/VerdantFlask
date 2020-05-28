from datetime import datetime

from bson import ObjectId, json_util
from flask import Flask
from flask.json import JSONEncoder

from root.blog.views import blog
from root.core.views import core
from root.error_pages.handlers import error_pages
from root.externals import db, login_manager
from root.users.views import users
from root.utils import extract_secret, get_secrets, set_environment_variables


class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def register_blueprints(app):
    """Register app blueprints with url prefix locations"""
    app.register_blueprint(core, url_prefix="")
    app.register_blueprint(users, url_prefix="/users")
    app.register_blueprint(blog, url_prefix="/blog")
    app.register_blueprint(error_pages, url_prefix="/error")


def create_app():

    secrets = get_secrets()
    set_environment_variables(extract_secret(secrets, "ENV_VARS"))
    config = extract_secret(secrets, "APP")

    # Initiate app
    app = Flask(__name__)
    app.json_encoder = MongoJsonEncoder

    # Update config from file
    app.config.update(config)

    # register blueprints
    register_blueprints(app)

    # initialize databases
    db.init_app(app)

    # initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "users.login"

    return app

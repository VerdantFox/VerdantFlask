from bson import json_util, ObjectId
from datetime import datetime
import os

from flask import Flask
from flask.json import JSONEncoder
import yaml

from root.externals import login_manager
from root.users.views import users
from root.externals import db
from root.core.views import core
from root.error_pages.handlers import error_pages


class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def get_config(path, production=False):
    """Gets a config file at the specified path and setting

    production: If true use "PROD" setting, else use "TEST"
    """
    setting = "PROD" if production is True else "TEST"
    config_path = os.path.abspath(os.path.join(path))
    with open(config_path) as conf:
        config_base = yaml.safe_load(conf)
        config = config_base[setting]

    return config


def create_app(config):
    # Initiate app
    app = Flask(__name__)
    app.json_encoder = MongoJsonEncoder

    # Update config file with MONGODB settings
    app.config.update(config)

    # register blueprints
    app.register_blueprint(core)
    app.register_blueprint(users)
    app.register_blueprint(error_pages)

    # initialize databases
    db.init_app(app)

    # initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "users.login"

    return app

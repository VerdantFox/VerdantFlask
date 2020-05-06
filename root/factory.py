from bson import json_util, ObjectId
from datetime import datetime
import os
from copy import deepcopy

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


def expand_mongo_config(config):
    """expand the mongo config to include multiple databases"""
    databases = ["flask", "slack", "test"]
    mongo_base_settings = config["MONGODB_SETTINGS"]
    config["MONGODB_SETTINGS"] = []
    for database in databases:
        new_setting = deepcopy(mongo_base_settings)
        new_setting["alias"] = f"{database}-alias"
        new_setting["db"] = database
        config["MONGODB_SETTINGS"].append(new_setting)
    return config


def create_app(config):
    # Initiate app
    app = Flask(__name__)
    app.json_encoder = MongoJsonEncoder

    # Update config file with MONGODB settings
    config = expand_mongo_config(config)
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

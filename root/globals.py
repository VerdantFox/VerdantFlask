"""Globals"""
import os

from flask_login import LoginManager
from flask_mongoengine import MongoEngine

# General Globals
SITE_WIDTH = 800  # TODO adjust this


# Paths
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_PATH = os.path.dirname(ROOT_PATH)
STATIC_PATH = os.path.join(ROOT_PATH, "static")

# Database setup
db = MongoEngine()

# Login manager setup
login_manager = LoginManager()

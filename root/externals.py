"""Globals"""
import os

from flask_login import LoginManager
from flask_mongoengine import MongoEngine

# Paths
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
STATIC_PATH = os.path.join(ROOT_PATH, "static")

# Database setup
db = MongoEngine()

# Login manager setup
login_manager = LoginManager()

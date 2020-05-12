"""Globals"""
from flask_login import LoginManager
from flask_mongoengine import MongoEngine

# Database setup
db = MongoEngine()

# Login manager setup
login_manager = LoginManager()

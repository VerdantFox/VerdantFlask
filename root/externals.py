from flask_mongoengine import MongoEngine
from flask_login import LoginManager

# Database setup
db = MongoEngine()

# Login manager setup
login_manager = LoginManager()

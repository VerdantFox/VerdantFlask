from flask_login import UserMixin
from werkzeug.security import check_password_hash

from src.globals import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class User(db.Document, UserMixin):
    """User model"""

    # User editable fields
    username = db.StringField(required=True, unique=True, max_length=40)
    email = db.EmailField(unique=True, required=False, sparse=True, max_length=80)
    share_email = db.BooleanField(default=False)
    password_hash = db.StringField(required=False)
    full_name = db.StringField(required=False, max_length=80)
    share_name = db.BooleanField(default=False)
    avatar_location = db.StringField(required=False, max_length=400)
    bio = db.StringField(required=False, max_length=1000)
    birth_date = db.DateTimeField(required=False)
    share_birth_date = db.BooleanField(default=False)
    timezone = db.StringField(required=False, max_length=80)
    share_timezone = db.BooleanField(default=False)

    # Access Levels (mostly for blog)
    # For now only editable by an admin with database access
    # 1. Admin
    # 2. Regular Users
    access_level = db.IntField(min_value=1, max_value=2, default=2)

    # Oauth stuff
    facebook_id = db.StringField(unique=True, required=False, sparse=True)
    google_id = db.StringField(unique=True, required=False, sparse=True)
    github_id = db.LongField(unique=True, required=False, sparse=True)

    meta = {
        "collection": "users",
        "indexes": [
            "username",
            "email",
            "password_hash",
            "share_email",
            "full_name",
            "share_name",
            "avatar_location",
            "bio",
            "birth_date",
            "share_birth_date",
            "timezone",
            "share_timezone",
            "access_level",
            "github_id",
            "facebook_id",
            "google_id",
        ],
    }

    def __str__(self):
        return f"User(username: {self.username}, id: {self.id})"

    def check_password(self, password: str) -> bool:
        """Checks that the pw provided hashes to the stored pw hash value"""
        return check_password_hash(self.password_hash, password)

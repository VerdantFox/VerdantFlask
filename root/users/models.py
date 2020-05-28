from flask_login import UserMixin
from werkzeug.security import check_password_hash

from root.externals import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class User(db.Document, UserMixin):
    """User model"""

    # User editable fields
    username = db.StringField(required=True, unique=True, max_length=30, index=True)
    email = db.EmailField(
        unique=True, required=False, sparse=True, max_length=80, index=True
    )
    share_email = db.BooleanField(required=True, default=False, index=True)
    password_hash = db.StringField(required=False, index=True)
    full_name = db.StringField(required=False, max_length=80, index=True)
    share_name = db.BooleanField(required=True, default=False, index=True)
    avatar_location = db.StringField(required=False, max_length=400, index=True)
    bio = db.StringField(required=False, max_length=1000, index=True)
    birth_date = db.DateTimeField(required=False, index=True)
    share_birth_date = db.BooleanField(required=True, default=False, index=True)
    timezone = db.StringField(required=False, max_length=80, index=True)
    share_timezone = db.BooleanField(required=True, default=False, index=True)

    # Access Levels (mostly for blog)
    # For now only editable by an admin with database access
    # 1. Admin
    # 2. Regular Users
    access_level = db.IntField(min_value=1, max_value=2, index=True)

    # Oauth stuff
    github_id = db.LongField(unique=True, required=False, sparse=True, index=True)
    facebook_id = db.StringField(unique=True, required=False, sparse=True, index=True)
    google_id = db.StringField(unique=True, required=False, sparse=True, index=True)

    meta = {
        "collection": "users",
        "indexes": [
            "username",
            "email",
            "full_name",
            "avatar_location",
            "bio",
            "birth_date",
            "timezone",
            "access_level",
            "github_id",
            "facebook_id",
            "google_id",
        ],
    }

    def __repr__(self):
        return f"Username: {self.username} id: {self.id}"

    def check_password(self, password):
        """Checks that the pw provided hashes to the stored pw hash value"""
        return check_password_hash(self.password_hash, password)

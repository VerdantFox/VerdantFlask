from flask_login import UserMixin
from werkzeug.security import check_password_hash

from root.externals import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class GithubToken(db.EmbeddedDocument):
    """GithubToken embedded document"""

    access_token = db.StringField(index=True)
    token_type = db.StringField(index=True)
    scope = db.ListField(db.StringField(), index=True)

    meta = {"indexes": ["access_token", "token_type", "scope"]}


class User(db.Document, UserMixin):
    """User model"""

    username = db.StringField(required=True, unique=True, max_length=30, index=True)
    email = db.EmailField(
        unique=True, required=False, sparse=True, max_length=80, index=True
    )
    password_hash = db.StringField(required=False, index=True)
    full_name = db.StringField(required=False, max_length=80, index=True)
    github_id = db.LongField(unique=True, required=False, sparse=True, index=True)
    github_name = db.StringField(required=False, index=True)
    facebook_id = db.StringField(unique=True, required=False, sparse=True, index=True)
    facebook_name = db.StringField(required=False, index=True)
    google_id = db.StringField(unique=True, required=False, sparse=True, index=True)
    google_name = db.StringField(required=False, index=True)

    meta = {
        "collection": "users",
        "indexes": [
            "username",
            "email",
            "full_name",
            "github_id",
            "github_name",
            "facebook_id",
            "facebook_name",
            "google_id",
            "google_name",
        ],
    }

    def __repr__(self):
        return f"Username: {self.username} id: {self.id}"

    def check_password(self, password):
        """Checks that the pw provided hashes to the stored pw hash value"""
        return check_password_hash(self.password_hash, password)

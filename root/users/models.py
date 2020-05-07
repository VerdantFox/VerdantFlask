from werkzeug.security import check_password_hash
from flask_login import UserMixin

from root.externals import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class User(db.Document, UserMixin):
    """User model"""

    username = db.StringField(
        required=True, unique=True, min_length=3, max_length=30, index=True
    )
    email = db.EmailField(required=True, unique=True, max_length=80, index=True)
    password_hash = db.StringField(required=True, index=True)
    full_name = db.StringField(required=False, max_length=80, index=True)

    meta = {
        "collection": "users",
        "indexes": ["username", "email"],
    }

    def __repr__(self):
        return f"Username: {self.username}, Email: {self.email}"

    def check_password(self, password):
        """Checks that the pw provided hashes to the stored pw hash value"""
        return check_password_hash(self.password_hash, password)

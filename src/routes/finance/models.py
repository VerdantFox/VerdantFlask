"""Blog models

Initial blog inspired by:
https://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/
"""

from bson.objectid import ObjectId

from src.globals import db


class Budget(db.Document):
    """Budget Model"""

    id = db.ObjectIdField(default=lambda: ObjectId(), primary_key=True)
    author = db.ObjectIdField(required=False)
    name = db.StringField(required=False, max_length=20)
    period = db.IntField(default=12)
    budget = db.DictField()

    meta = {
        "collection": "budget",
        "indexes": ["author", "name"],
    }

    def __str__(self):
        return f"Budget(id: {self.id}, author: {self.author}, name: {self.name})"

"""Blog models

Initial blog inspired by:
https://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/
"""

# from bson.objectid import ObjectId

from src.globals import db


class Budget(db.DynamicDocument):
    """Budget Model"""

    author = db.ObjectIdField(required=True)
    name = db.StringField(required=True, max_length=30)
    slug = db.StringField()

    meta = {
        "collection": "budget",
        "indexes": ["author", "name"],
    }

    def __str__(self):
        return f"Budget(author: {self.author}, name: {self.name})"

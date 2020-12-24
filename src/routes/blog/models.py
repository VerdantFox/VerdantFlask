"""Blog models

Initial blog inspired by:
https://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/
"""

from bson.objectid import ObjectId

from src.globals import db


class Reply(db.EmbeddedDocument):
    """Reply to comment embedded document"""

    id = db.ObjectIdField(default=lambda: ObjectId())
    author = db.ObjectIdField(required=True)
    content = db.StringField(required=True, max_length=500)
    created_timestamp = db.DateTimeField(required=True)
    updated_timestamp = db.DateTimeField(required=True)
    likes = db.IntField(default=0)


class Comment(db.EmbeddedDocument):
    """Comment embedded document"""

    id = db.ObjectIdField(default=lambda: ObjectId())
    author = db.ObjectIdField(required=True)
    content = db.StringField(required=True, max_length=500)
    created_timestamp = db.DateTimeField(required=True)
    updated_timestamp = db.DateTimeField(required=True)
    likes = db.IntField(default=0)
    replies = db.EmbeddedDocumentListField(Reply, required=False)


class Image(db.EmbeddedDocument):
    """Image embedded document"""

    name = db.StringField(required=False, default="image name")
    location = db.StringField(required=True)


class BlogPost(db.Document):
    """Blog post model"""

    title = db.StringField(required=True, unique=True, max_length=80)
    slug = db.StringField(required=True, unique=True, max_length=80)
    author = db.ObjectIdField(required=True)
    published = db.BooleanField(required=True, default=False)
    tags = db.ListField(db.StringField(), required=False)
    markdown_description = db.StringField(required=True, max_length=50_000)
    markdown_content = db.StringField(required=True, max_length=500_000)
    html_description = db.StringField(required=True)
    html_content = db.StringField(required=True)
    images = db.EmbeddedDocumentListField(Image, required=False)
    created_timestamp = db.DateTimeField(required=True)
    updated_timestamp = db.DateTimeField(required=True)
    likes = db.IntField(default=0)
    views = db.IntField(default=0)
    can_comment = db.BooleanField(default=True)
    comments = db.EmbeddedDocumentListField(Comment, required=False)

    meta = {
        "collection": "blog",
        "indexes": [
            {
                "fields": ["$title", "$author", "$tags", "$markdown_content"],
                "default_language": "english",
                "weights": {
                    "author": 20,
                    "tags": 15,
                    "title": 10,
                    "markdown_content": 2,
                },
            },
            "title",
            "slug",
            "author",
            "published",
            "tags",
            "created_timestamp",
            "updated_timestamp",
            "likes",
            "views",
            "can_comment",
            "comments.id",
            "comments.author",
            "comments.created_timestamp",
            "comments.updated_timestamp",
            "comments.likes",
            "comments.replies.id",
            "comments.replies.author",
            "comments.replies.created_timestamp",
            "comments.replies.updated_timestamp",
            "comments.replies.likes",
        ],
    }

    def __str__(self):
        return (
            f"Post(title: {self.title}, author: {self.author}, "
            f"published: {self.published})"
        )

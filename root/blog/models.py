"""Blog models

Initial blog inspired by:
https://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/
"""

from bson.objectid import ObjectId

from root.externals import db


class Reply(db.EmbeddedDocument):
    """Reply to comment embedded document"""

    id = db.ObjectIdField(default=lambda: ObjectId(), index=True)
    author = db.ObjectIdField(required=True, index=True)
    content = db.StringField(required=True, max_length=500)
    created_timestamp = db.DateTimeField(required=True, index=True)
    updated_timestamp = db.DateTimeField(required=True, index=True)

    meta = {"indexes": ["author"]}


class Comment(db.EmbeddedDocument):
    """Comment embedded document"""

    id = db.ObjectIdField(default=lambda: ObjectId(), index=True)
    author = db.ObjectIdField(required=True, index=True)
    content = db.StringField(required=True, max_length=500)
    created_timestamp = db.DateTimeField(required=True, index=True)
    updated_timestamp = db.DateTimeField(required=True, index=True)
    replies = db.EmbeddedDocumentListField(Reply, required=False, index=True)

    meta = {"indexes": ["author", "replies"]}


class BlogPost(db.Document):
    """Blog post model"""

    title = db.StringField(required=True, unique=True, max_length=80, index=True)
    slug = db.StringField(required=True, unique=True, max_length=80, index=True)
    author = db.ObjectIdField(required=True, index=True)
    published = db.BooleanField(required=True, default=False, index=True)
    tags = db.ListField(db.StringField(index=True), required=False, index=True)
    markdown_description = db.StringField(required=True, max_length=5_000)
    markdown_content = db.StringField(required=True, max_length=30_000)
    html_description = db.StringField(required=True)
    html_content = db.StringField(required=True)
    image_locations = db.ListField(db.StringField(), required=False)
    created_timestamp = db.DateTimeField(required=True, index=True)
    updated_timestamp = db.DateTimeField(required=True, index=True)
    comments = db.EmbeddedDocumentListField(Comment, required=False, index=True)

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
            "published",
            "author",
            "created_timestamp",
            "updated_timestamp",
            "tags",
            "comments",
            "comments.author",
            "comments.replies",
            "comments.replies.author",
        ],
    }

    def __repr__(self):
        return (
            f"Post(title: {self.title}, author: {self.author}, "
            f"published: {self.published})"
        )

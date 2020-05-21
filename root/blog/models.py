"""Blog models

Initial blog inspired by:
https://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/
"""

from bson.objectid import ObjectId
from flask import (
    Flask,
    Markup,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

from root.externals import SITE_WIDTH, db

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())


class Reply(db.EmbeddedDocument):
    """Reply to comment embedded document"""

    reply_id = db.ObjectIdField(default=lambda: ObjectId(), index=True)
    author = db.ObjectIdField(index=True)
    content = db.StringField(required=True)
    created_timestamp = db.DateTimeField(required=True, index=True)
    updated_timestamp = db.DateTimeField(required=True, index=True)

    meta = {"indexes": ["author"]}


class Comment(db.EmbeddedDocument):
    """Comment embedded document"""

    comment_id = db.ObjectIdField(default=lambda: ObjectId(), index=True)
    author = db.ObjectIdField(required=False, index=True)
    content = db.StringField(required=True)
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
    thumbnail_location = db.StringField(required=False)
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

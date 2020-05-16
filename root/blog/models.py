"""Blog models

Some code borrowed and altered for my purposes from this blog post:
https://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/
"""
import datetime
import functools
import os
import re

import bleach
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
    published = db.BooleanField(required=True, default=False, index=True)
    author = db.ObjectIdField(required=True, index=True)
    markdown_content = db.StringField(required=True, max_length=10_000)
    html_preview = db.StringField(required=True)
    html_content = db.StringField(required=True)
    image_locations = db.ListField(db.StringField(), required=False)
    created_timestamp = db.DateTimeField(required=True, index=True)
    updated_timestamp = db.DateTimeField(required=True, index=True)
    comments = db.EmbeddedDocumentListField(Comment, required=False, index=True)
    tags = db.ListField(db.StringField(index=True), required=False, index=True)

    meta = {
        "collection": "blog",
        "indexes": [
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
        return f"Post: {self.title} author: {self.author}"

    @staticmethod
    def html_content(markdown_content):
        """
        Generate HTML representation of the markdown-formatted blog entry,
        and also convert any media URLs into rich media objects such as video
        players or images.
        """
        hilite = CodeHiliteExtension(linenums=False, css_class="highlight")
        extras = ExtraExtension()
        markdown_content = markdown(markdown_content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content, oembed_providers, urlize_all=True, maxwidth=SITE_WIDTH,
        )
        return Markup(oembed_content)

    @staticmethod
    def sanitize_markup(markup):
        bleach.clean(markup)

    def update_slug(self, *args, **kwargs):
        """Generate slug from entries title"""
        if not self.slug:
            self.slug = re.sub(r"[^\w]+", "-", self.title.lower()).strip("-")

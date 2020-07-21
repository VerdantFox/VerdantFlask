"""Pytest configuration file for blog functional tests"""
import datetime

import pytest
from bson.objectid import ObjectId

from root.routes.blog.models import BlogPost

DATE = datetime.datetime.now() - datetime.timedelta(7)
BP1_PUBLISHED = {
    "title": "Post 1",
    "slug": "post-1",
    "author": ObjectId(),
    "tags": ["tag1", "tag2"],
    "markdown_description": "# BP 1 description",
    "markdown_content": "# BP 1 content",
    "html_description": "<h1>BP 1 description</h1>",
    "html_content": "<h1>BP 1 content</h1>",
    "created_timestamp": DATE,
    "updated_timestamp": DATE,
    "published": True,
    "comments": [
        {
            "author": ObjectId(),
            "content": "BP comment",
            "created_timestamp": DATE + datetime.timedelta(1),
            "updated_timestamp": DATE + datetime.timedelta(1),
            "replies": [
                {
                    "author": ObjectId(),
                    "content": "BP reply",
                    "created_timestamp": DATE + datetime.timedelta(2),
                    "updated_timestamp": DATE + datetime.timedelta(2),
                }
            ],
        }
    ],
}
BP2_PUBLISHED = {
    "title": "Post 2",
    "slug": "post-2",
    "author": ObjectId(),
    "tags": ["tag2", "tag3"],
    "markdown_description": "# BP 2 description",
    "markdown_content": "# BP 2 content",
    "html_description": "<h1>BP 2 description</h1>",
    "html_content": "<h1>BP 2 content</h1>",
    "created_timestamp": DATE + datetime.timedelta(1),
    "updated_timestamp": DATE + datetime.timedelta(1),
    "published": True,
}
BP3_UNPUBLISHED = {
    "title": "Post 3",
    "slug": "post-3",
    "author": ObjectId(),
    "tags": ["tag4", "tag5"],
    "markdown_description": "# BP 3 description",
    "markdown_content": "# BP 3 content",
    "html_description": "<h1>BP 3 description</h1>",
    "html_content": "<h1>BP 3 content</h1>",
    "created_timestamp": DATE + datetime.timedelta(2),
    "updated_timestamp": DATE + datetime.timedelta(2),
    # "published": False,
}


@pytest.fixture(scope="module")
def load_3_bp_mod(client_module):
    """Loads 2 blogposts into database"""
    bp1 = BlogPost(**BP1_PUBLISHED)
    bp1.save()
    bp2 = BlogPost(**BP2_PUBLISHED)
    bp2.save()
    bp3 = BlogPost(**BP3_UNPUBLISHED)
    bp3.save()

    yield bp1, bp2, bp3

    bp1 = BlogPost.objects(id=bp1.id)
    bp1.delete()
    bp2 = BlogPost.objects(id=bp2.id)
    bp2.delete()
    bp3 = BlogPost.objects(id=bp3.id)
    bp3.delete()

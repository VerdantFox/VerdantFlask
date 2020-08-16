"""Pytest configuration file for blog functional tests"""
import datetime

import pytest
from bson.objectid import ObjectId

from root.routes.blog.models import BlogPost
from tests.conftest import STANDARD_USER

DATE = datetime.datetime.now() - datetime.timedelta(7)
BP1_PUBLISHED = {
    "title": "Post 1",
    "slug": "post-1",
    "author": ObjectId(),
    "tags": ["tag1", "tag2"],
    "markdown_description": "# BP 1 description",
    "markdown_content": "# BP 1 content. Reasonable.",
    "html_description": "<h1>BP 1 description.</h1>",
    "html_content": "<h1>BP 1 content. Reasonable.</h1>",
    "created_timestamp": DATE,
    "updated_timestamp": DATE,
    "published": True,
    "comments": [
        {
            "author": STANDARD_USER["id"],
            "content": "BP comment",
            "created_timestamp": DATE + datetime.timedelta(1),
            "updated_timestamp": DATE + datetime.timedelta(1),
            "replies": [
                {
                    "author": STANDARD_USER["id"],
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
    "markdown_content": "# BP 2 content. Crazy.",
    "html_description": "<h1>BP 2 description</h1>",
    "html_content": "<h1>BP 2 content. Crazy.</h1>",
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
    "published": False,
}
BP4_PUBLISHED_COMMENTS_LOCKED = {
    "title": "Post 4",
    "slug": "post-4",
    "author": ObjectId(),
    "tags": ["tag2", "tag3"],
    "markdown_description": "# BP 4 description",
    "markdown_content": "# BP 4 content. Crazy.",
    "html_description": "<h1>BP 4 description</h1>",
    "html_content": "<h1>BP 4 content. Crazy.</h1>",
    "created_timestamp": DATE + datetime.timedelta(1),
    "updated_timestamp": DATE + datetime.timedelta(1),
    "published": True,
    "can_comment": False,
}
BP5_BP1_BUT_COMMENTS_LOCKED = {
    "title": "Post 1",
    "slug": "post-1",
    "author": ObjectId(),
    "tags": ["tag1", "tag2"],
    "markdown_description": "# BP 1 description",
    "markdown_content": "# BP 1 content. Reasonable.",
    "html_description": "<h1>BP 1 description.</h1>",
    "html_content": "<h1>BP 1 content. Reasonable.</h1>",
    "created_timestamp": DATE,
    "updated_timestamp": DATE,
    "published": True,
    "can_comment": False,
    "comments": [
        {
            "author": STANDARD_USER["id"],
            "content": "BP comment",
            "created_timestamp": DATE + datetime.timedelta(1),
            "updated_timestamp": DATE + datetime.timedelta(1),
            "replies": [
                {
                    "author": STANDARD_USER["id"],
                    "content": "BP reply",
                    "created_timestamp": DATE + datetime.timedelta(2),
                    "updated_timestamp": DATE + datetime.timedelta(2),
                }
            ],
        }
    ],
}


@pytest.fixture(scope="module")
def load_3_bp_mod(client_module):
    """Loads 3 blogposts into database"""
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


@pytest.fixture
def bp1():
    """Load blogpost 1"""
    bp1 = BlogPost(**BP1_PUBLISHED)
    bp1.save()

    yield bp1

    bp1 = BlogPost.objects(id=bp1.id)
    bp1.delete()


@pytest.fixture
def bp2():
    """Load blogpost 2"""
    bp2 = BlogPost(**BP2_PUBLISHED)
    bp2.save()

    yield bp2

    bp2 = BlogPost.objects(id=bp2.id)
    bp2.delete()


@pytest.fixture
def bp3():
    """Load blogpost 3"""
    bp3 = BlogPost(**BP3_UNPUBLISHED)
    bp3.save()

    yield bp3

    bp3 = BlogPost.objects(id=bp3.id)
    bp3.delete()


@pytest.fixture
def bp4():
    """Load blogpost 4"""
    bp4 = BlogPost(**BP4_PUBLISHED_COMMENTS_LOCKED)
    bp4.save()

    yield bp4

    bp4 = BlogPost.objects(id=bp4.id)
    bp4.delete()


@pytest.fixture
def bp5():
    """Load blogpost 4"""
    bp5 = BlogPost(**BP5_BP1_BUT_COMMENTS_LOCKED)
    bp5.save()

    yield bp5

    bp5 = BlogPost.objects(id=bp5.id)
    bp5.delete()

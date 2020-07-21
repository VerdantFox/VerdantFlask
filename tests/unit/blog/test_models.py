"""Most basic pytest"""
import datetime

import mongoengine
import pytest
from bson.objectid import ObjectId

from root.routes.blog.models import BlogPost
from tests.mongodb_helpers import list_indexes

BLOG_COLLECTION = "blog"
BLOG_MODEL_DEFAULTS = {
    # field: [default, indexed]
    "title": [None, True],
    "slug": [None, True],
    "author": [None, True],
    "published": [False, True],
    "tags": [[], True],
    "markdown_description": [None, False],
    "markdown_content": [None, False],
    "html_description": [None, False],
    "html_content": [None, False],
    "image_locations": [[], False],
    "created_timestamp": [None, True],
    "updated_timestamp": [None, True],
    "likes": [0, True],
    "views": [0, True],
    "can_comment": [True, True],
    "comments.id": [ObjectId(), True],
    "comments.author": [None, True],
    "comments.content": [None, False],
    "comments.created_timestamp": [None, True],
    "comments.updated_timestamp": [None, True],
    "comments.likes": [0, True],
    "comments.replies.id": [ObjectId(), True],
    "comments.replies.author": [None, True],
    "comments.replies.content": [None, False],
    "comments.replies.created_timestamp": [None, True],
    "comments.replies.updated_timestamp": [None, True],
    "comments.replies.likes": [0, True],
}
NOW = datetime.datetime.now()
GOOD_BLOGPOSTS = [
    pytest.param(
        {
            "title": "Full Blog Title",
            "slug": "full-blog-title",
            "author": ObjectId(),
            "published": True,
            "tags": ["tag1", "tag2", "tag3"],
            "markdown_description": "# Cool blog post",
            "markdown_content": "## some other cool stuff",
            "html_description": "<h1>Cool blog post</h1>",
            "html_content": "<h2>some other cool stuff</h2>",
            "image_locations": ["/location/1", "location/2"],
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
            "likes": 5,
            "views": 123,
            "comments": [
                {
                    "id": ObjectId(),
                    "author": ObjectId(),
                    "content": "I like your post",
                    "created_timestamp": NOW,
                    "updated_timestamp": NOW,
                    "likes": 3,
                    "replies": [
                        {
                            "id": ObjectId(),
                            "author": ObjectId(),
                            "content": "replying to comment",
                            "created_timestamp": NOW,
                            "updated_timestamp": NOW,
                            "likes": 1,
                        }
                    ],
                }
            ],
        },
        id="everything",
    ),
    pytest.param(
        {
            "title": "Minimal Title",
            "slug": "minimal-title",
            "author": ObjectId(),
            "markdown_description": "# Cool blog post",
            "markdown_content": "## some other cool stuff",
            "html_description": "<h1>Cool blog post</h1>",
            "html_content": "<h2>some other cool stuff</h2>",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
        },
        id="minimal",
    ),
    pytest.param(
        {
            "title": "Minimal Title",
            "slug": "minimal-title",
            "author": ObjectId(),
            "markdown_description": "# Cool blog post",
            "markdown_content": "## some other cool stuff",
            "html_description": "<h1>Cool blog post</h1>",
            "html_content": "<h2>some other cool stuff</h2>",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
            "comments": [
                {
                    "author": ObjectId(),
                    "content": "I like your post",
                    "created_timestamp": NOW,
                    "updated_timestamp": NOW,
                    "replies": [
                        {
                            "author": ObjectId(),
                            "content": "replying to comment",
                            "created_timestamp": NOW,
                            "updated_timestamp": NOW,
                        }
                    ],
                }
            ],
        },
        id="minimal_comment",
    ),
]


def assert_equals_or_default(dict_val, post_val, default):
    """assert equality or default with some normalization"""
    if dict_val is None:
        if isinstance(default, type(ObjectId())):
            assert isinstance(post_val, type(ObjectId()))
        else:
            assert post_val in [default, "NO_CHECK"]
    elif isinstance(dict_val, datetime.date):
        assert str(post_val).split(".")[0] == str(dict_val).split(".")[0]
    else:
        assert post_val == dict_val


def get_vals_and_defaults(key, dictionary, post):
    """Get dictionary values and defaults"""
    default = BLOG_MODEL_DEFAULTS[key][0]
    indexed = BLOG_MODEL_DEFAULTS[key][1]
    key_split = key.split(".")
    if len(key_split) == 1:
        dict_val = dictionary[key] if key in dictionary else None
        post_val = post[key] if key in post else None
    elif len(key_split) == 2:
        if "comments" in dictionary and len(dictionary["comments"]) > 0:
            dict_val = dictionary[key_split[0]][-1].get(key_split[1])
        else:
            dict_val = "NO_CHECK"
        post_val = (
            post[key_split[0]][-1][key_split[1]]
            if len(post["comments"]) > 0
            else "NO_CHECK"
        )
    elif len(key_split) == 3:
        if (
            "comments" in dictionary
            and len(dictionary["comments"]) > 0
            and "replies" in dictionary["comments"][-1]
            and len(dictionary["comments"][-1]["replies"]) > 0
        ):
            dict_val = dictionary[key_split[0]][-1][key_split[1]][-1].get(key_split[2])
        else:
            dict_val = "NO_CHECK"
        if (
            "comments" in post
            and len(post["comments"]) > 0
            and "replies" in post["comments"][-1]
            and len(post["comments"][-1]["replies"]) > 0
        ):
            post_val = post[key_split[0]][-1][key_split[1]][-1][key_split[2]]
        else:
            post_val = "NO_CHECK"
    return key, dict_val, post_val, default, indexed


@pytest.mark.parametrize("bp_dict", GOOD_BLOGPOSTS)
def test_new_blogpost_good_succeeds(client, delete_blogposts, bp_dict):
    """
    GIVEN a BlogPost model
    WHEN a new BlogPost is created
    THEN check the fields are created correctly
    """
    post = BlogPost(**bp_dict)
    post.save()
    post = BlogPost.objects(id=post.id).first()
    assert (
        str(post)
        == f"Post(title: {post.title}, author: {post.author}, published: {post.published})"
    )
    indexs_found = set(list_indexes(BLOG_COLLECTION))
    for key in BLOG_MODEL_DEFAULTS:
        key, dict_val, post_val, default, indexed = get_vals_and_defaults(
            key, bp_dict, post
        )
        assert_equals_or_default(dict_val, post_val, default)
        if indexed is True:
            assert key in indexs_found


BAD_POSTS = [
    pytest.param(
        {
            "title": "a" * 81,
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
        },
        id="title_too_long",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "a" * 81,
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
        },
        id="slug_too_long",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": "Author is string",
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
        },
        id="author_is_string",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "tags": "tag1,tag2",
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
        },
        id="tags_is_string",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "image_locations": "loc1",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
        },
        id="image_loc_is_string",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": "BadMonth 2, 2013",
            "updated_timestamp": NOW,
        },
        id="created_timestamp_bad",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": "BadMonth 2, 2013",
        },
        id="updated_timestamp_is_str",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
            "comments": [
                {
                    "author": ObjectId(),
                    "content": "a" * 501,
                    "created_timestamp": NOW,
                    "updated_timestamp": NOW,
                }
            ],
        },
        id="long_comment",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
            "comments": [
                {
                    "author": "author_string",
                    "content": "a" * 501,
                    "created_timestamp": NOW,
                    "updated_timestamp": NOW,
                }
            ],
        },
        id="comment_author_string",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
            "comments": [
                {
                    "author": ObjectId(),
                    "content": "string",
                    "created_timestamp": NOW,
                    "updated_timestamp": NOW,
                    "replies": [
                        {
                            "author": ObjectId(),
                            "content": "a" * 501,
                            "created_timestamp": NOW,
                            "updated_timestamp": NOW,
                        }
                    ],
                }
            ],
        },
        id="long_reply",
    ),
    pytest.param(
        {
            "title": "string",
            "slug": "string",
            "author": ObjectId(),
            "markdown_description": "string",
            "markdown_content": "string",
            "html_description": "string",
            "html_content": "string",
            "created_timestamp": NOW,
            "updated_timestamp": NOW,
            "comments": [
                {
                    "author": ObjectId(),
                    "content": "string",
                    "created_timestamp": NOW,
                    "updated_timestamp": NOW,
                    "replies": [
                        {
                            "author": "author_string",
                            "content": "replying to comment",
                            "created_timestamp": NOW,
                            "updated_timestamp": NOW,
                        }
                    ],
                }
            ],
        },
        id="reply_author_string",
    ),
]


@pytest.mark.parametrize("bp_dict", BAD_POSTS)
def test_new_post_bad_fails(client, delete_blogposts, bp_dict):
    """
    GIVEN a BlogPost model
    WHEN a new BlogPost is created
    THEN check post fails when fields don't match model rules
    """
    new_bp = BlogPost(**bp_dict)
    with pytest.raises(mongoengine.errors.ValidationError):
        new_bp.save()

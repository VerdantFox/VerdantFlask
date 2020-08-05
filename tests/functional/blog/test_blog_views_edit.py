"""Test blog edit view"""
import pytest

from root.routes.blog.models import BlogPost
from root.utils import get_slug, list_from_string

form_model_mapper = {
    "next_page": None,
    "title": "title",
    "tags": "tags",
    "publish": "published",
    "can_comment": "can_comment",
    "description": "markdown_description",
    "content": "markdown_content",
}


def test_blog_edit_get_not_logged_in_fails(client, delete_blogposts, bp1):
    """Test GET of blogpost edit fails with login redirect"""
    response = client.get(f"/blog/edit/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data


def test_blog_edit_get_no_admin_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test GET of blogpost edit fails with 401 for non-admin user"""
    response = client.get(f"/blog/edit/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 403
    data = response.data.decode()
    assert "Only admin can edit post." in data


def test_blog_edit_get_non_existant_post_fails(
    client, current_user_admin, delete_blogposts
):
    """Test GET of blogpost edit fails with 404 if slug not found"""
    response = client.get("/blog/edit/some-nonexistant-post", follow_redirects=True)
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data


def test_blog_edit_get_admin_happy(client, current_user_admin, delete_blogposts, bp1):
    """Test GET of the blog edit route as admin user who owns post succeeds"""
    response = client.get(f"/blog/edit/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Edit Blog Post</h1>" in data
    assert bp1.title in data


HAPPY_FORMS = [
    pytest.param(
        {
            "next_page": "view",
            "title": "Edited title",
            "tags": "tag1_edit,tag2_edit",
            "publish": True,
            "can_comment": True,
            "description": "# short description edited",
            "content": "# short content edited",
        },
        id="view_True",
    ),
    pytest.param(
        {
            "next_page": "edit",
            "title": "Edited title 2",
            "tags": "tag1_edit",
            "publish": False,
            "can_comment": False,
            "description": "# short description 2 edited",
            "content": "# short content 2 edited",
        },
        id="edit_False",
    ),
    pytest.param(
        {
            "next_page": "nonsense",
            "title": "Edited title 2",
            "tags": "tag1_edited",
            "publish": False,
            "can_comment": False,
            "description": "# short description 3 edited",
            "content": "# short content 3 edited",
        },
        id="next_is_nonsense",
    ),
]


@pytest.mark.parametrize("form_data", HAPPY_FORMS)
def test_blog_edit_submit_happy(
    client, current_user_admin, delete_blogposts, bp1, form_data
):
    """Test POST of blog with happy form"""
    form_data_copy = form_data.copy()
    for field, val in form_data_copy.items():
        if val is False:
            form_data.pop(field)
    response = client.post(
        f"/blog/edit/{bp1.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    if form_data.get("next_page") == "edit":
        assert (
            '<li class="breadcrumb-item active" aria-current="page">Edit</li>' in data
        )
    else:
        assert (
            '<li class="breadcrumb-item active" aria-current="page">View Post</li>'
            in data
        )
    slug = get_slug(form_data.get("title"))
    post = BlogPost.objects(slug=slug).first()
    for form_field, form_val in form_data_copy.items():
        model_field = form_model_mapper[form_field]
        if model_field is None:
            continue
        elif model_field == "tags":
            form_val = list_from_string(form_val)
        assert form_val == post[model_field]


BAD_FORMS = [
    pytest.param(
        {
            "next_page": "view",
            "title": "a" * 201,
            "tags": "tag1_edited,tag2_edited",
            "publish": True,
            "can_comment": True,
            "description": "# short description edited",
            "content": "# short content edited",
        },
        "Field cannot be longer than 200 characters.",
        id="long_title",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "",
            "tags": "tag1_edited,tag2_edited",
            "publish": True,
            "can_comment": True,
            "description": "# short description edited",
            "content": "# short content edited",
        },
        "This field is required.",
        id="missing_title",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Edited title",
            "tags": "a" * 201,
            "publish": True,
            "can_comment": True,
            "description": "# short description edited",
            "content": "# short content edited",
        },
        "Field cannot be longer than 200 characters.",
        id="long_tags",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Edited title",
            "tags": "tag1_edited,tag2_edited",
            "publish": True,
            "can_comment": True,
            "description": "a" * 50_001,
            "content": "# short content edited",
        },
        "Field cannot be longer than 50000 characters.",
        id="long_description",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Edited title",
            "tags": "tag1_edited,tag2_edited",
            "publish": True,
            "can_comment": True,
            "description": "",
            "content": "# short content edited",
        },
        "This field is required.",
        id="missing_description",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Edited title",
            "tags": "tag1_edited,tag2_edited",
            "publish": True,
            "can_comment": True,
            "description": "# short description edited",
            "content": "a" * 500_001,
        },
        "Field cannot be longer than 500000 characters.",
        id="long_content",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Edited title",
            "tags": "tag1_edited,tag2_edited",
            "publish": True,
            "can_comment": True,
            "description": "# short description edited",
            "content": "",
        },
        "This field is required.",
        id="missing_content",
    ),
]


@pytest.mark.parametrize("form_data, err_msg", BAD_FORMS)
def test_blog_edit_submit_bad_forms_fail(
    client, current_user_admin, delete_blogposts, bp1, form_data, err_msg
):
    """Test POST of blog with bad forms fails"""
    form_data_copy = form_data.copy()
    for field, val in form_data_copy.items():
        if val is False:
            form_data.pop(field)
    response = client.post(
        f"/blog/edit/{bp1.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Error editing post!" in data
    assert err_msg in data
    edited_slug = get_slug(form_data.get("title"))
    edited_post = BlogPost.objects(slug=edited_slug).first()
    assert edited_post is None
    old_post = BlogPost.objects(slug=bp1.slug).first()
    assert old_post is not None
    assert old_post == bp1

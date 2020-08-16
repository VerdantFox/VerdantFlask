"""Test blog create view"""
import pytest

from src.routes.blog.models import BlogPost
from src.utils import get_slug, list_from_string
from tests.functional.blog.conftest import BP1_PUBLISHED

form_model_mapper = {
    "next_page": None,
    "title": "title",
    "tags": "tags",
    "publish": "published",
    "can_comment": "can_comment",
    "description": "markdown_description",
    "content": "markdown_content",
}


def test_blog_create_get_not_logged_in_fails(client, delete_blogposts):
    """Test GET of blogpost create fails with login redirect"""
    response = client.get("/blog/create", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data


def test_blog_create_get_no_admin_fails(
    client, current_user_standard, delete_blogposts
):
    """Test GET of blogpost create fails with 401 for non-admin user"""
    response = client.get("/blog/create", follow_redirects=True)
    assert response.status_code == 401
    data = response.data.decode()
    assert "Blog create page requires admin access." in data


def test_blog_create_get_admin(client, current_user_admin, delete_blogposts):
    """Test GET of the blog create route as admin user"""
    response = client.get("/blog/create", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Create Blog Post</h1>" in data


HAPPY_FORMS = [
    pytest.param(
        {
            "next_page": "view",
            "title": "Brand New BP",
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "# short description",
            "content": "# short content",
        },
        id="view_True",
    ),
    pytest.param(
        {
            "next_page": "edit",
            "title": "Brand New BP 2",
            "tags": "tag1",
            "publish": False,
            "can_comment": False,
            "description": "# short description 2",
            "content": "# short content 2",
        },
        id="edit_False",
    ),
    pytest.param(
        {
            "next_page": "nonsense",
            "title": "Brand New BP 2",
            "tags": "tag1",
            "publish": False,
            "can_comment": False,
            "description": "# short description 2",
            "content": "# short content 2",
        },
        id="next_is_nonsense",
    ),
]


@pytest.mark.parametrize("form_data", HAPPY_FORMS)
def test_blog_create_submit_happy(
    client, current_user_admin, delete_blogposts, bp1, form_data
):
    """Test POST of blog with happy form"""
    form_data_copy = form_data.copy()
    for field, val in form_data_copy.items():
        if val is False:
            form_data.pop(field)
    response = client.post("/blog/create", data=form_data, follow_redirects=True)
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
            "title": BP1_PUBLISHED["title"],
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "# short description unique",
            "content": "# short content",
        },
        "Title must be unique",
        id="title_duplicate",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "a" * 201,
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "# short description",
            "content": "# short content",
        },
        "Field cannot be longer than 200 characters.",
        id="long_title",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "",
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "# short description",
            "content": "# short content",
        },
        "This field is required.",
        id="missing_title",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Brand New BP",
            "tags": "a" * 201,
            "publish": True,
            "can_comment": True,
            "description": "# short description",
            "content": "# short content",
        },
        "Field cannot be longer than 200 characters.",
        id="long_tags",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Brand New BP",
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "a" * 50_001,
            "content": "# short content",
        },
        "Field cannot be longer than 50000 characters.",
        id="long_description",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Brand New BP",
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "",
            "content": "# short content",
        },
        "This field is required.",
        id="missing_description",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Brand New BP",
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "# short description",
            "content": "a" * 500_001,
        },
        "Field cannot be longer than 500000 characters.",
        id="long_content",
    ),
    pytest.param(
        {
            "next_page": "view",
            "title": "Brand New BP",
            "tags": "tag1,tag2",
            "publish": True,
            "can_comment": True,
            "description": "# short description",
            "content": "",
        },
        "This field is required.",
        id="missing_content",
    ),
]


@pytest.mark.parametrize("form_data, err_msg", BAD_FORMS)
def test_blog_create_submit_bad_forms_fail(
    client, current_user_admin, delete_blogposts, bp1, form_data, err_msg
):
    """Test POST of blog with bad forms fails"""
    form_data_copy = form_data.copy()
    for field, val in form_data_copy.items():
        if val is False:
            form_data.pop(field)
    response = client.post("/blog/create", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Error creating post!" in data
    assert err_msg in data
    slug = get_slug(form_data.get("title"))
    post = BlogPost.objects(slug=slug).first()
    if form_data["title"] != BP1_PUBLISHED["title"]:
        assert post is None
    else:
        assert post.markdown_description != form_data["description"]

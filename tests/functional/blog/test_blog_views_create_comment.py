"""Test blog create reply view"""
from root.routes.blog.models import BlogPost


def test_blog_create_comment_not_logged_in_fails(client, delete_blogposts, bp2):
    """Test comment create while not logged in fails with login redirect"""
    form_data = {"comment": "Cool post!"}
    response = client.post(
        f"/blog/comment/{bp2.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data
    bp2 = BlogPost.objects(id=bp2.id).first()
    assert not bp2.comments


def test_blog_create_comment_non_existant_post_fails(
    client, current_user_standard, delete_blogposts
):
    """Test comment create fails with 404 if slug not found"""
    form_data = {"comment": "Cool post!"}
    response = client.post(
        "/blog/comment/some-nonexistant-post", data=form_data, follow_redirects=True
    )
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data


def test_blog_comment_too_long_fails(
    client, current_user_standard, delete_blogposts, bp2
):
    """Test too long comment fails"""
    form_data = {"comment": "A" * 501}
    response = client.post(
        f"/blog/comment/{bp2.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Field cannot be longer than 500 characters." in data
    bp2 = BlogPost.objects(id=bp2.id).first()
    assert not bp2.comments


def test_blog_create_comment_comments_locked_fails(
    client, current_user_standard, delete_blogposts, bp4
):
    """Test comment fails if comments locked"""
    form_data = {"comment": "Cool post!"}
    response = client.post(
        f"/blog/comment/{bp4.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Commenting is locked for this post." in data
    assert "Commenting has been closed for this post." in data
    bp4 = BlogPost.objects(id=bp4.id).first()
    assert not bp4.comments


def test_blog_create_comment_happy(
    client, current_user_standard, delete_blogposts, bp2
):
    """Test comment create succeeds"""
    form_data = {"comment": "Cool post!"}
    response = client.post(
        f"/blog/comment/{bp2.slug}", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Cool post!" in data
    bp2 = BlogPost.objects(id=bp2.id).first()
    assert bp2.comments

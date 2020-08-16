"""Test blog delete view"""
from root.routes.blog.models import BlogPost


def test_blog_delete_not_logged_in_fails(client, delete_blogposts, bp1):
    """Test GET of blogpost delete fails with login redirect"""
    response = client.get(f"/blog/delete/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data
    assert "Deleted post" not in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1


def test_blog_delete_no_admin_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test GET of blogpost delete fails with 403 for non-admin user"""
    response = client.get(f"/blog/delete/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 403
    data = response.data.decode()
    assert "Only admin can edit post." in data
    assert "Deleted post" not in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1


def test_blog_delete_non_existant_post_fails(
    client, current_user_admin, delete_blogposts
):
    """Test GET of blogpost delete fails with 404 if slug not found"""
    response = client.get("/blog/delete/some-nonexistant-post", follow_redirects=True)
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data
    assert "Deleted post" not in data


def test_blog_delete_happy(client, current_user_admin, delete_blogposts, bp1):
    """Test GET of the blog delete route as admin user succeeds"""
    response = client.get(f"/blog/delete/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Deleted post '{bp1.slug}'!".replace("'", "&#39;") in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert not bp1

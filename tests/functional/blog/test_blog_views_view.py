"""Test blog view view"""


def test_blog_view_get_standard(client, delete_blogposts_mod, bp1):
    """Test standard GET of the blog view route"""
    response = client.get(f"/blog/view/{bp1.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert bp1.title in data


def test_blog_view_get_hidden_as_admin_succeeds(
    client, current_user_admin, delete_blogposts_mod, bp3
):
    """Test GET of the view route of hidden blogpost as admin user succeeds"""
    response = client.get(f"/blog/view/{bp3.slug}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert bp3.title in data


def test_blog_view_get_hidden_as_non_admin_fails(
    client, current_user_standard, delete_blogposts_mod, bp3
):
    """Test GET of the view route of hidden blogpost as non-admin user fails"""
    response = client.get(f"/blog/view/{bp3.slug}", follow_redirects=True)
    assert response.status_code == 401
    data = response.data.decode()
    assert (
        "This post is unpublished. Only admin can view it, sorry. Check back later!"
        in data
    )

"""Test blog tags view"""


def test_blog_tags_get_standard(client, delete_blogposts_mod, load_3_bp_mod):
    """Test standard GET of the blog tags route"""
    response = client.get("/blog/tags")
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Blog Entries by Tag</h1>" in data
    tags_dict = {}
    for post in load_3_bp_mod:
        if post.published is True:
            for tag in post.tags:
                if tag in tags_dict:
                    tags_dict[tag] += 1
                else:
                    tags_dict[tag] = 1
    for tag, count in tags_dict.items():
        assert f'<a href="/blog/?tag={tag}">{tag}</a> ({count})'


def test_blog_tags_get_admin(
    client, current_user_admin, delete_blogposts_mod, load_3_bp_mod
):
    """Test GET of the blog tags route as admin user"""
    response = client.get("/blog/tags")
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Blog Entries by Tag</h1>" in data
    tags_dict = {}
    for post in load_3_bp_mod:
        for tag in post.tags:
            if tag in tags_dict:
                tags_dict[tag] += 1
            else:
                tags_dict[tag] = 1
    for tag, count in tags_dict.items():
        assert f'<a href="/blog/?tag={tag}">{tag}</a> ({count})'

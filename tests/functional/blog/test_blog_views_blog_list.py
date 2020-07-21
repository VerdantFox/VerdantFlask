"""Test blog list view"""


def test_blog_list_get_standard(client, delete_blogposts_mod, load_3_bp_mod):
    """Test standard GET of the blog_list route"""
    posts = load_3_bp_mod
    response = client.get("/blog", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    for post in posts:
        title_anchor = f'<a href="/blog/view/{post.slug}">{post.title}</a>'
        if post.published is True:
            assert title_anchor in data
            assert post.created_timestamp.strftime("%B %d, %Y %I:%M %p") in data
            assert f"{len(post.comments)} comments" in data
            for tag in post.tags:
                assert f'<a href="/blog/?tag={tag}">{tag}</a>' in data
        else:
            assert title_anchor not in data

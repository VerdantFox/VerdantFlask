"""Test blog list view"""


def test_blog_list_get_standard(client, delete_blogposts_mod, load_3_bp_mod):
    """Test standard GET of the blog_list route"""
    response = client.get("/blog", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "[unpublished]" not in data
    for post in load_3_bp_mod:
        title_anchor = f'<a href="/blog/view/{post.slug}">{post.title}</a>'
        if post.published is True:
            assert title_anchor in data
            assert post.created_timestamp.strftime("%B %d, %Y %I:%M %p") in data
            assert f"{len(post.comments)} comments" in data
            for tag in post.tags:
                assert f'<a href="/blog/?tag={tag}">{tag}</a>' in data
        else:
            assert title_anchor not in data


def test_blog_list_get_admin(
    client, current_user_admin, delete_blogposts_mod, load_3_bp_mod
):
    """Test GET of the blog_list route as admin user"""
    response = client.get("/blog", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    unpublished_posts = []
    for post in load_3_bp_mod:
        if post.published is not True:
            unpublished_posts.append(post)
        title_anchor = f'<a href="/blog/view/{post.slug}">{post.title}</a>'
        assert title_anchor in data
        assert post.created_timestamp.strftime("%B %d, %Y %I:%M %p") in data
        assert f"{len(post.comments)} comments" in data
        for tag in post.tags:
            assert f'<a href="/blog/?tag={tag}">{tag}</a>' in data
    assert data.count("[unpublished]") == len(unpublished_posts)


def test_blog_list_get_tags(client, delete_blogposts_mod, load_3_bp_mod):
    """Test GET of the blog_list route with tag selected"""
    for post_outer in load_3_bp_mod:
        if post_outer.published is not True:
            continue
        for tag_outer in post_outer.tags:
            response = client.get(f"/blog?tag={tag_outer}", follow_redirects=True)
            assert response.status_code == 200
            data = response.data.decode()
            assert f"| tag: '{tag_outer}'" in data
            for post_inner in load_3_bp_mod:
                title_anchor = (
                    f'<a href="/blog/view/{post_inner.slug}">{post_inner.title}</a>'
                )
                if tag_outer in post_inner.tags and post_inner.published is True:
                    assert title_anchor in data
                    assert (
                        post_inner.created_timestamp.strftime("%B %d, %Y %I:%M %p")
                        in data
                    )
                    assert f"{len(post_inner.comments)} comments" in data
                    for tag_inner in post_inner.tags:
                        assert (
                            f'<a href="/blog/?tag={tag_inner}">{tag_inner}</a>' in data
                        )
                else:
                    assert title_anchor not in data


def test_blog_list_get_search(client, delete_blogposts_mod, load_3_bp_mod):
    """Test standard GET of the blog_list route"""
    response = client.get("/blog?search=crazy", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    bp1, bp2, bp3 = load_3_bp_mod
    assert f'<a href="/blog/view/{bp2.slug}">{bp2.title}</a>' in data
    assert f'<a href="/blog/view/{bp1.slug}">{bp1.title}</a>' not in data

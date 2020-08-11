"""Test blog edit view"""
from root.routes.blog.models import BlogPost


def test_blog_edit_comment_not_logged_in_fails(client, delete_blogposts, bp1):
    """Test comment edit while not logged in fails with login redirect"""
    comment_edit = "Updated comment"
    form_data = {"comment": comment_edit}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/edit/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert comment_edit not in data
    assert "Please log in to access this page." in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].content != comment_edit


def test_blog_edit_comment_non_existant_post_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test comment edit fails with 404 if slug not found"""
    comment_edit = "Updated comment"
    form_data = {"comment": comment_edit}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/some-nonexistant-post/edit/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].content != comment_edit


def test_blog_edit_comment_non_existant_no_change(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test comment edit of non-existant comment_id results in no change"""
    comment_edit = "Updated comment"
    form_data = {"comment": comment_edit}
    response = client.post(
        f"/blog/comment/{bp1.slug}/edit/randomid", data=form_data, follow_redirects=True
    )
    assert response.status_code == 200
    bp1_after = BlogPost.objects(id=bp1.id).first()
    assert bp1_after == bp1


def test_blog_comment_edit_too_long_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test too long comment fails fails"""
    comment_edit = "A" * 501
    form_data = {"comment": comment_edit}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/edit/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Field cannot be longer than 500 characters." in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].content != comment_edit


def test_blog_edit_comment_comments_locked_fails(
    client, current_user_standard, delete_blogposts, bp5
):
    """Test comment fails if comments locked"""
    comment_edit = "Updated comment"
    form_data = {"comment": comment_edit}
    comment_id = bp5.comments[0].id
    response = client.post(
        f"/blog/comment/{bp5.slug}/edit/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Commenting is locked for this post." in data
    assert "Commenting has been closed for this post." in data
    bp5 = BlogPost.objects(id=bp5.id).first()
    assert bp5.comments[0].content != comment_edit


def test_blog_comment_edit_wrong_user_fails(
    client, current_user_admin, delete_blogposts, bp1
):
    """Test too long comment fails"""
    comment_edit = "Updated comment"
    form_data = {"comment": comment_edit}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/edit/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Can only edit your own comment!" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].content != comment_edit


def test_blog_edit_comment_happy(client, current_user_standard, delete_blogposts, bp1):
    """Test comment create succeeds"""
    comment_edit = "Updated comment"
    form_data = {"comment": comment_edit}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/edit/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].content == comment_edit

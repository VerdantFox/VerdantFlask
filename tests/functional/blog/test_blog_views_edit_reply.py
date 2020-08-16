"""Test blog edit comment view"""
from root.routes.blog.models import BlogPost


def test_blog_edit_reply_not_logged_in_fails(client, delete_blogposts, bp1):
    """Test reply edit while not logged in fails with login redirect"""
    reply_edit = "updated reply"
    form_data = {"comment": reply_edit}
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/edit/{reply_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert reply_edit not in data
    assert "Please log in to access this page." in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies[0].content != reply_edit


def test_blog_edit_reply_non_existant_post_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test reply edit fails with 404 if slug not found"""
    reply_edit = "updated reply"
    form_data = {"comment": reply_edit}
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/some-nonexistant-post/reply/{comment_id}/edit/{reply_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies[0].content != reply_edit


def test_blog_edit_reply_comment_non_existant_no_change(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test reply edit of non-existant comment_id results in no change"""
    reply_edit = "updated reply"
    form_data = {"comment": reply_edit}
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/randomid/edit/{reply_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    bp1_after = BlogPost.objects(id=bp1.id).first()
    assert bp1_after == bp1


def test_blog_edit_reply_reply_non_existant_no_change(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test reply edit of non-existant reply_id results in no change"""
    reply_edit = "updated reply"
    form_data = {"comment": reply_edit}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/edit/randomid",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    bp1_after = BlogPost.objects(id=bp1.id).first()
    assert bp1_after == bp1


def test_blog_reply_edit_too_long_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test too long comment fails fails"""
    reply_edit = "A" * 501
    form_data = {"comment": reply_edit}
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/edit/{reply_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Field cannot be longer than 500 characters." in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies[0].content != reply_edit


def test_blog_edit_reply_comments_locked_fails(
    client, current_user_standard, delete_blogposts, bp5
):
    """Test reply fails if comments locked"""
    reply_edit = "updated reply"
    form_data = {"comment": reply_edit}
    comment_id = bp5.comments[0].id
    reply_id = bp5.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp5.slug}/reply/{comment_id}/edit/{reply_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Commenting is locked for this post." in data
    assert "Commenting has been closed for this post." in data
    bp5 = BlogPost.objects(id=bp5.id).first()
    assert bp5.comments[0].replies[0].content != reply_edit


def test_blog_reply_edit_wrong_user_fails(
    client, current_user_admin, delete_blogposts, bp1
):
    """Test edit comment as non-owner fails"""
    reply_edit = "updated reply"
    form_data = {"comment": reply_edit}
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/edit/{reply_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Can only edit your own reply!" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies[0].content != reply_edit


def test_blog_edit_reply_happy(client, current_user_standard, delete_blogposts, bp1):
    """Test reply edit succeeds"""
    reply_edit = "updated reply"
    form_data = {"comment": reply_edit}
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/edit/{reply_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies[0].content == reply_edit

"""Test blog delete comment view"""
from src.routes.blog.models import BlogPost


def test_blog_delete_reply_not_logged_in_fails(client, delete_blogposts, bp1):
    """Test reply delete while not logged in fails with login redirect"""
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/delete/{reply_id}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies


def test_blog_delete_reply_non_existant_post_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test reply delete fails with 404 if slug not found"""
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/some-nonexistant-post/reply/{comment_id}/delete/{reply_id}",
        follow_redirects=True,
    )
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies


def test_blog_delete_reply_comment_non_existant_no_change(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test reply delete of non-existant comment_id results in no change"""
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/randomid/delete/{reply_id}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies


def test_blog_delete_reply_non_existant_no_change(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test reply delete of non-existant reply_id results in no change"""
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/delete/randomid",
        follow_redirects=True,
    )
    assert response.status_code == 200
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies


def test_blog_delete_reply_comments_locked_fails(
    client, current_user_standard, delete_blogposts, bp5
):
    """Test delete reply fails if comments locked"""
    comment_id = bp5.comments[0].id
    reply_id = bp5.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp5.slug}/reply/{comment_id}/delete/{reply_id}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Commenting is locked for this post." in data
    assert "Commenting has been closed for this post." in data
    bp5 = BlogPost.objects(id=bp5.id).first()
    assert bp5.comments[0].replies


def test_blog_reply_delete_wrong_user_fails(
    client, current_user_admin, delete_blogposts, bp1
):
    """Test delete reply as non-owner fails"""
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/delete/{reply_id}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Can only delete your own reply!" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert bp1.comments[0].replies


def test_blog_delete_reply_happy(client, current_user_standard, delete_blogposts, bp1):
    """Test reply delete succeeds"""
    comment_id = bp1.comments[0].id
    reply_id = bp1.comments[0].replies[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}/delete/{reply_id}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    bp1 = BlogPost.objects(id=bp1.id).first()
    assert not bp1.comments[0].replies

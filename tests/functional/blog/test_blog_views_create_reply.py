"""Test blog create reply view"""
from src.routes.blog.models import BlogPost


def test_blog_create_reply_not_logged_in_fails(client, delete_blogposts, bp1):
    """Test reply create while not logged in fails with login redirect"""
    reply_count_before = len(bp1.comments[0].replies)
    form_data = {"comment": "New reply"}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    reply_count_after = len(bp1.comments[0].replies)
    assert reply_count_before == reply_count_after


def test_blog_create_reply_non_existant_post_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test comment create fails with 404 if slug not found"""
    reply_count_before = len(bp1.comments[0].replies)
    form_data = {"comment": "New reply"}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/some-nonexistant-post/reply/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 404
    data = response.data.decode()
    assert "Blog post not found!" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    reply_count_after = len(bp1.comments[0].replies)
    assert reply_count_before == reply_count_after


def test_blog_reply_too_long_fails(
    client, current_user_standard, delete_blogposts, bp1
):
    """Test too long reply fails"""
    reply_count_before = len(bp1.comments[0].replies)
    form_data = {"comment": "A" * 501}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Field cannot be longer than 500 characters." in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    reply_count_after = len(bp1.comments[0].replies)
    assert reply_count_before == reply_count_after


def test_blog_create_reply_comments_locked_fails(
    client, current_user_standard, delete_blogposts, bp5
):
    """Test reply fails if comments locked"""
    reply_count_before = len(bp5.comments[0].replies)
    form_data = {"comment": "New reply"}
    comment_id = bp5.comments[0].id
    response = client.post(
        f"/blog/comment/{bp5.slug}/reply/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "Commenting is locked for this post." in data
    assert "Commenting has been closed for this post." in data
    bp5 = BlogPost.objects(id=bp5.id).first()
    reply_count_after = len(bp5.comments[0].replies)
    assert reply_count_before == reply_count_after


def test_blog_create_reply_happy(client, current_user_standard, delete_blogposts, bp1):
    """Test reply create succeeds"""
    reply_count_before = len(bp1.comments[0].replies)
    form_data = {"comment": "New reply"}
    comment_id = bp1.comments[0].id
    response = client.post(
        f"/blog/comment/{bp1.slug}/reply/{comment_id}",
        data=form_data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert "New reply" in data
    bp1 = BlogPost.objects(id=bp1.id).first()
    reply_count_after = len(bp1.comments[0].replies)
    assert reply_count_after == reply_count_before + 1

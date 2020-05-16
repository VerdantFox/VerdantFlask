from flask import (
    Blueprint,
    Markup,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from root.blog.forms import CommentForm, EditBlogPostForm, SearchForm
from root.blog.models import BlogPost
from root.utils import setup_pagination

blog = Blueprint("blog", __name__)


@blog.route("/blog", methods=["GET", "POST"])
def blog_list():
    """Get a timestamp ordered list of blog posts to display with search

    TODO show unpublished to author but not to public
    """
    form = SearchForm()
    if form.validate_on_submit():
        query = form.search.data
        if query:
            posts = BlogPost.search_text(query)
    elif request.method == "GET":
        posts = BlogPost.objects()
    limit_fields = ["title", "slug", "author", "html_preview", "created_timestamp"]
    posts = posts.only(*limit_fields).order_by("created_timestamp")
    results_per_page = 20  # Maybe set with form in future
    paginator = setup_pagination(form.page.data, results_per_page, posts)
    return render_template("blog/list_posts.html", form=form, paginator=paginator)


@blog.route("/blog/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new blogpost"""
    form = EditBlogPostForm()
    return "HI"


@blog.route("/blog/view/<slug>", methods=["GET"])
def view():
    """Display an individual blogpost"""
    pass


@blog.route("/blog/update/<slug>", methods=["GET", "POST"])
@login_required
def update(slug):
    """Update a blogpost"""
    form = EditBlogPostForm()
    form.slug.data = slug


@blog.route("/blog/delete/<slug>", methods=["POST"])
@login_required
def delete(slug):
    """Delete a blogpost"""
    pass


@blog.route("/blog/comment/<slug>", methods=["POST"])
@login_required
def comment(slug):
    """Comment on a blogpost"""
    form = CommentForm()
    pass


@blog.route("/blog/comment/<slug>/edit/<comment_id>", methods=["POST"])
@login_required
def edit_comment(slug, comment_id):
    """Edit comment"""
    form = CommentForm()
    pass


@blog.route("/blog/comment/<slug>/delete/<comment_id>", methods=["POST"])
@login_required
def delete_comment(slug, comment_id):
    """Delete comment"""
    pass


@blog.route("/blog/comment/<slug>/reply/<comment_id>", methods=["POST"])
def reply(slug, comment_id):
    """Reply to comment"""
    form = CommentForm()
    pass


@blog.route("/blog/comment/<slug>/reply/<comment_id>/edit/<reply_id>", methods=["POST"])
def edit_reply(slug, comment_id, reply_id):
    """Edit reply to comment"""
    form = CommentForm()
    pass


@blog.route(
    "/blog/comment/<slug>/reply/<comment_id>/delete/<reply_id>", methods=["POST"]
)
def delete_reply(slug, comment_id, reply_id):
    """Delete reply to comment"""
    pass


# ----------------------------------------------------------------------------
# HELPER METHODS
# ----------------------------------------------------------------------------
def create_or_edit(form, post, template):
    """Create or edit a blog post"""

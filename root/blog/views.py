import datetime
import functools
import os
import re

from flask import (
    Blueprint,
    Markup,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

from root.blog.forms import CommentForm, CreateBlogPostForm, EditBlogPostForm
from root.blog.models import BlogPost
from root.externals import SITE_WIDTH
from root.utils import get_slug, list_from_string, setup_pagination

blog = Blueprint("blog", __name__)

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())


@blog.route("/blog", methods=["GET"])
def blog_list():
    """Get a timestamp ordered list of blog posts to display with search

    TODO show unpublished to author but not to public
    """
    search = request.args.get("search")
    try:
        page = int(request.args.get("page"))
    except (ValueError, TypeError):
        page = 0

    query = {}
    if current_user.access_level != 1:
        query["published"] = True

    posts = BlogPost.objects(**query)
    if search:
        posts = posts.search_text(search)

    limit_fields = ["title", "slug", "author", "html_preview", "created_timestamp"]
    posts = posts.only(*limit_fields).order_by("created_timestamp")
    results_per_page = 20  # Maybe set with form in future
    paginator = setup_pagination(page, results_per_page, posts)
    return render_template("blog/list_posts.html", paginator=paginator,)


@blog.route("/blog/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new blogpost"""
    if current_user.access_level != 1:
        abort(401, f"Blog create page requires admin access.")

    form = CreateBlogPostForm()
    if form.validate_on_submit():
        return create_or_edit(form=form, title=form.title.data)
    elif form.errors:
        flash("Error creating post!", category="error")

    return render_template("blog/create_post.html", form=form,)


@blog.route("/blog/view/<slug>", methods=["GET"])
def view(slug):
    """Display an individual blogpost"""
    post = BlogPost.objects(slug=slug).first()
    if not post:
        abort(404, "Blog post not found!")
    if post.published is False:
        if not current_user.is_authenticated or current_user.access_level != 1:
            abort(
                401,
                "This post is unpublished. Only admin can view it, "
                "sorry. Check back later!",
            )
    return render_template("blog/view_post.html")


@blog.route("/blog/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit(slug):
    """Update a blogpost"""
    form = EditBlogPostForm()
    form.slug.data = slug
    return "in UPDATE"


@blog.route("/blog/delete/<slug>", methods=["POST"])
@login_required
def delete(slug):
    """Delete a blogpost"""
    return "in DELETE"


@blog.route("/blog/comment/<slug>", methods=["POST"])
@login_required
def create_comment(slug):
    """Comment on a blogpost"""
    form = CommentForm()
    return "in comment CREATE"


@blog.route("/blog/comment/<slug>/edit/<comment_id>", methods=["POST"])
@login_required
def edit_comment(slug, comment_id):
    """Edit comment"""
    form = CommentForm()
    return "in comment EDIT"


@blog.route("/blog/comment/<slug>/delete/<comment_id>", methods=["POST"])
@login_required
def delete_comment(slug, comment_id):
    """Delete comment"""
    return "in comment DELETE"


@blog.route("/blog/comment/<slug>/reply/<comment_id>", methods=["POST"])
def create_reply(slug, comment_id):
    """Reply to comment"""
    form = CommentForm()
    return "in reply CREATE"


@blog.route("/blog/comment/<slug>/reply/<comment_id>/edit/<reply_id>", methods=["POST"])
def edit_reply(slug, comment_id, reply_id):
    """Edit reply to comment"""
    form = CommentForm()
    return "in reply EDIT"


@blog.route(
    "/blog/comment/<slug>/reply/<comment_id>/delete/<reply_id>", methods=["POST"]
)
def delete_reply(slug, comment_id, reply_id):
    """Delete reply to comment"""
    return "in reply DELETE"


# ----------------------------------------------------------------------------
# HELPER METHODS
# ----------------------------------------------------------------------------
def create_or_edit(form, title, edit=False):
    """Create or edit a blog post"""
    slug = get_slug(title)
    # Slug is the True test of unique-ness
    post = BlogPost.objects(slug=slug).first()
    if edit is False:
        if post:
            flash("Post with that title already exists", category="error")
            return render_template("blog/create_post.html", form=form,)
        post = BlogPost()

    post.title = form.title.data
    post.slug = get_slug(post.title)
    post.author = current_user.id
    post.published = form.publish.data
    post.tags = list_from_string(form.tags.data)
    form.tags.data = ",".join(post.tags)
    post.markdown_content = form.content.data.strip()
    post.html_content = get_html(post.markdown_content)
    markdown_preview = post.markdown_content[:100]
    # Use 1500 after testing
    post.html_preview = get_html(markdown_preview)
    post.thumbnail_location = form.thumbnail.data.strip()
    post.image_locations = list_from_string(form.images.data)
    form.images.data = ",".join(post.image_locations)
    if edit is False:
        post.created_timestamp = datetime.datetime.now()
    post.updated_timestamp = datetime.datetime.now()
    post.save()
    return redirect(url_for("blog.view", slug=post.slug))


def get_html(markdown_content):
    """
    Generate HTML representation of the markdown-formatted blog entry,
    and also convert any media URLs into rich media objects such as video
    players or images.
    """
    hilite = CodeHiliteExtension(linenums=False, css_class="highlight")
    extras = ExtraExtension()
    markdown_content = markdown(markdown_content, extensions=[hilite, extras])
    oembed_content = parse_html(
        markdown_content, oembed_providers, urlize_all=True, maxwidth=SITE_WIDTH,
    )
    return Markup(oembed_content)

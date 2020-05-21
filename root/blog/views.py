import datetime
import functools
import os
import re
from collections import OrderedDict

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
    """Get a timestamp ordered list of blog posts to display with search"""
    search = request.args.get("search")
    tag = request.args.get("tag")
    query = {}
    if tag:
        query["tags"] = tag

    try:
        page = int(request.args.get("page"))
    except (ValueError, TypeError):
        page = 0
    results_per_page = 20  # Maybe set with form in future

    paginator = query_and_paginate_blog(
        query=query, search=search, page=page, results_per_page=results_per_page
    )

    return render_template("blog/list_posts.html", paginator=paginator, tag=tag, search=search)


@blog.route("/blog/tags", methods=["GET"])
def tags():
    """List tags and associated counts of blogs"""

    tag_counts = get_current_tags(False)

    return render_template("blog/tags.html", tag_counts=tag_counts)


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
    return render_template("blog/view_post.html", post=post)


@blog.route("/blog/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit(slug):
    """Update a blogpost"""
    # Slug is the True test of unique-ness
    post = BlogPost.objects(slug=slug).first()
    if post.author != current_user.id:
        abort(403, f"Only blogpost author can edit post.")

    form = EditBlogPostForm()

    if form.validate_on_submit():
        return create_or_edit(form=form, title=form.title.data, post=post)
    elif form.errors:
        flash("Error editing post!", category="error")

    form.title.data = post.title
    form.tags.data = ",".join(post.tags)
    form.publish.data = post.published
    form.description.data = post.markdown_description
    form.content.data = post.markdown_content
    form.images.data = ",".join(post.image_locations)

    return render_template("blog/edit_post.html", form=form,)


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
def query_and_paginate_blog(query=None, search=None, page=1, results_per_page=3):
    """Query database on params and return paginator object

    Params:
        query: dictionary of mongoengine query parameters
        search: string used to search against database
    Returns:
        mongoengine paginator object
    """
    if not query:
        query = {}
    query["published"] = True
    if current_user.is_authenticated and current_user.access_level == 1:
        query.pop("published")
    posts = BlogPost.objects(**query)
    if search:
        posts = posts.search_text(search)
    limit_fields = [
        "title",
        "slug",
        "author",
        "tags",
        "html_description",
        "created_timestamp",
        "published",
        "comments",
    ]
    posts = posts.only(*limit_fields).order_by("-created_timestamp")
    return setup_pagination(page, results_per_page, posts)


def create_or_edit(form, title, post=None):
    """Create or edit a blog post"""
    if post is None:
        edit = False
    else:
        edit = True

    if edit is False:
        if post:
            flash("Post with that title already exists", category="error")
            return render_template("blog/create_post.html", form=form)
        post = BlogPost()

    post.title = form.title.data
    post.slug = get_slug(post.title)
    post.author = current_user.id
    post.published = form.publish.data
    post.tags = list_from_string(form.tags.data)
    post.markdown_content = form.content.data.strip()
    post.html_content = get_html(post.markdown_content)
    post.markdown_description = form.description.data.strip()
    post.html_description = get_html(post.markdown_description)
    post.thumbnail_location = form.thumbnail.data.strip()
    post.image_locations = list_from_string(form.images.data)
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


def get_current_tags(only_published=True):
    """Return an ordered dictionary """
    query = {"published": True}
    if current_user.is_authenticated and current_user.access_level == 1:
        query.pop("published")
    limit_fields = [
        "tags",
    ]
    posts = BlogPost.objects(**query).only(*limit_fields)
    all_tags = set(posts.distinct("tags"))
    all_tags.discard(None)
    all_tags = list(all_tags)
    all_tags.sort()
    tag_counts = dict()
    for tag in all_tags:
        tag_counts[tag] = 0
    for post in posts:
        for tag in post.tags:
            tag_counts[tag] += 1
    # Sort by count after already sorted by tag
    tag_counts = OrderedDict(sorted(tag_counts.items(), key=lambda x: -x[1]))
    return tag_counts

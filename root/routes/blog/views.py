from collections import OrderedDict
from datetime import datetime

from flask import (
    Blueprint,
    Markup,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.toc import TocExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

from root.globals import SITE_WIDTH
from root.image_handler import delete_blog_image, upload_blog_image
from root.routes.blog.forms import (
    CommentForm,
    CreateBlogPostForm,
    EditBlogPostForm,
    EditImagesForm,
)
from root.routes.blog.models import BlogPost, Comment, Reply
from root.routes.users.models import User
from root.utils import get_slug, list_from_string, setup_pagination

blog = Blueprint("blog", __name__)

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())


@blog.route("/", methods=["GET"])
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

    return render_template(
        "blog/list_posts.html", paginator=paginator, tag=tag, search=search
    )


@blog.route("/tags", methods=["GET"])
def tags():
    """List tags and associated counts of blogs"""

    tag_counts = get_current_tags(False)

    return render_template("blog/tags.html", tag_counts=tag_counts)


@blog.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new blogpost"""
    if current_user.access_level != 1:
        abort(401, "Blog create page requires admin access.")

    form = CreateBlogPostForm()
    if form.validate_on_submit():
        return create_or_edit(form=form, title=form.title.data)
    elif form.errors:
        flash("Error creating post!", category="error")

    return render_template("blog/create_post.html", form=form,)


@blog.route("/view/<slug>", methods=["GET", "POST"])
def view(slug):
    """Display an individual blogpost"""
    form = CommentForm()
    post = get_post_for_view(slug)
    comment_authors = get_comment_authors(post)
    return render_template(
        "blog/view_post.html", post=post, comment_authors=comment_authors, form=form
    )


@blog.route("/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit(slug):
    """Update a blogpost"""
    post = get_post_for_update_delete(slug)
    form = EditBlogPostForm()

    if form.validate_on_submit():
        return create_or_edit(form=form, title=form.title.data, post=post)
    elif form.errors:
        flash("Error editing post!", category="error")

    form.title.data = post.title
    form.tags.data = ",".join(post.tags)
    form.can_comment.data = post.can_comment
    form.publish.data = post.published
    form.description.data = post.markdown_description
    form.content.data = post.markdown_content
    form.next_page.data = None

    return render_template("blog/edit_post.html", form=form, post=post)


@blog.route("/edit_images/<slug>", methods=["GET", "POST"])
@login_required
def edit_images(slug):
    """Edit images at blogpost"""
    post = get_post_for_update_delete(slug)
    form = EditImagesForm()
    if form.upload_image.data:
        blog_image = upload_blog_image(form.upload_image.data)
        if blog_image is None:
            flash("Invalid image extension type used!")
        else:
            blog_image_location = url_for(
                "static", filename=f"images/blog_uploaded/{blog_image}"
            )
            post.image_locations.append(blog_image_location)
            post.save()
            return redirect(url_for("blog.edit_images", slug=slug))
    if form.delete_image.data:
        post.update(pull__image_locations=form.delete_image.data)
        post.save()
        delete_blog_image(form.delete_image.data)
        return redirect(url_for("blog.edit_images", slug=slug))

    return render_template("blog/edit_images.html", form=form, post=post)


@blog.route("/delete/<slug>", methods=["GET"])
@login_required
def delete(slug):
    """Delete a blogpost"""
    post = get_post_for_update_delete(slug)
    post.delete()
    flash(f"Deleted post '{slug}'!")
    return redirect(url_for("blog.blog_list"))


@blog.route("/comment/<slug>", methods=["POST"])
@login_required
def create_comment(slug):
    """Comment on a blogpost"""
    form = CommentForm()
    post = get_post_for_view(slug)
    failed_comment_id = None
    comment_error = None
    if post.can_comment:
        if form.validate_on_submit() and form.comment.data:
            comment = Comment(
                author=current_user.id,
                content=str(form.comment.data).strip(),
                created_timestamp=datetime.now(),
                updated_timestamp=datetime.now(),
            )
            post.comments.append(comment)
            post.comments = sort_comments(post.comments)
            post.save()
        if not form.validate_on_submit() and form.comment.errors:
            failed_comment_id = "primary"
            comment_error = form.comment.errors[0]
    else:
        flash("Commenting is locked for this post.", category="error")
    comment_authors = get_comment_authors(post)
    return render_template(
        "blog/comments/comments.html",
        post=post,
        comment_authors=comment_authors,
        form=form,
        failed_comment_id=failed_comment_id,
        comment_error=comment_error,
    )


@blog.route("/comment/<slug>/edit/<comment_id>", methods=["POST"])
@login_required
def edit_comment(slug, comment_id):
    """Edit comment"""
    form = CommentForm()
    post = get_post_for_view(slug)
    failed_comment_id = None
    comment_error = None
    if post.can_comment:
        if form.validate_on_submit() and form.comment.data:
            for comment in post.comments:
                if comment.author != current_user.id:
                    failed_comment_id = comment_id
                    comment_error = "Can only edit your own comment!"
                    break
                if str(comment.id) == comment_id:
                    comment.content = str(form.comment.data).strip()
                    comment.updated_timestamp = datetime.now()
                    post.save()
                    break
        if not form.validate_on_submit() and form.comment.errors:
            failed_comment_id = comment_id
            comment_error = form.comment.errors[0]
    else:
        flash("Commenting is locked for this post.", category="error")
    comment_authors = get_comment_authors(post)
    return render_template(
        "blog/comments/comments.html",
        post=post,
        comment_authors=comment_authors,
        form=form,
        failed_comment_id=failed_comment_id,
        comment_error=comment_error,
    )


@blog.route("/comment/<slug>/delete/<comment_id>", methods=["POST"])
@login_required
def delete_comment(slug, comment_id):
    """Delete comment"""
    form = CommentForm()
    post = get_post_for_view(slug)
    index = None
    failed_comment_id = None
    comment_error = None
    if post.can_comment:
        for i, comment in enumerate(post.comments):
            if str(comment.id) == comment_id:
                if comment.author == current_user.id:
                    index = i
                else:
                    failed_comment_id = comment_id
                    comment_error = "Can only edit your own comment!"
                break
        if index is not None:
            post.comments.pop(index)
            post.save()
    else:
        flash("Commenting is locked for this post.", category="error")
    comment_authors = get_comment_authors(post)
    return render_template(
        "blog/comments/comments.html",
        post=post,
        comment_authors=comment_authors,
        form=form,
        failed_comment_id=failed_comment_id,
        comment_error=comment_error,
    )


@blog.route("/comment/<slug>/reply/<comment_id>", methods=["POST"])
def create_reply(slug, comment_id):
    """Reply to comment"""
    form = CommentForm()
    post = get_post_for_view(slug)
    failed_comment_id = None
    comment_error = None
    if post.can_comment:
        if form.validate_on_submit() and form.comment.data:
            for comment in post.comments:
                if str(comment.id) == comment_id:
                    reply = Reply(
                        author=current_user.id,
                        content=str(form.comment.data).strip(),
                        created_timestamp=datetime.now(),
                        updated_timestamp=datetime.now(),
                    )
                    comment.replies.append(reply)
                    post.save()
                    break
        if not form.validate_on_submit() and form.comment.errors:
            failed_comment_id = comment_id
            comment_error = form.comment.errors[0]
    else:
        flash("Commenting is locked for this post.", category="error")
    comment_authors = get_comment_authors(post)
    return render_template(
        "blog/comments/comments.html",
        post=post,
        comment_authors=comment_authors,
        form=form,
        failed_comment_id=failed_comment_id,
        comment_error=comment_error,
    )


@blog.route("/comment/<slug>/reply/<comment_id>/edit/<reply_id>", methods=["POST"])
def edit_reply(slug, comment_id, reply_id):
    """Edit reply to comment"""
    form = CommentForm()
    post = get_post_for_view(slug)
    failed_comment_id = None
    comment_error = None
    if post.can_comment:
        if form.validate_on_submit() and form.comment.data:
            for comment in post.comments:
                if str(comment.id) == comment_id:
                    for reply in comment.replies:
                        if str(reply.id) == reply_id:
                            if reply.author == current_user.id:
                                reply.content = str(form.comment.data).strip()
                                reply.updated_timestamp = datetime.now()
                                post.save()
                            else:
                                failed_comment_id = reply_id
                                comment_error = "Can only edit your own reply!"
                            break
                    break
        if not form.validate_on_submit() and form.comment.errors:
            failed_comment_id = reply_id
            comment_error = form.comment.errors[0]
    else:
        flash("Commenting is locked for this post.", category="error")
    comment_authors = get_comment_authors(post)
    return render_template(
        "blog/comments/comments.html",
        post=post,
        comment_authors=comment_authors,
        form=form,
        failed_comment_id=failed_comment_id,
        comment_error=comment_error,
    )


@blog.route(
    "/blog/comment/<slug>/reply/<comment_id>/delete/<reply_id>", methods=["POST"]
)
def delete_reply(slug, comment_id, reply_id):
    """Delete reply to comment"""
    form = CommentForm()
    post = get_post_for_view(slug)
    comment_index = None
    reply_index = None
    failed_comment_id = None
    comment_error = None
    if post.can_comment:
        for i, comment in enumerate(post.comments):
            if str(comment.id) == comment_id:
                for j, reply in enumerate(comment.replies):
                    if str(reply.id) == reply_id:
                        if reply.author == current_user.id:
                            comment_index = i
                            reply_index = j
                        else:
                            failed_comment_id = reply_id
                            comment_error = "Can only delete your own reply!"
                        break
                break
        if reply_index is not None:
            post.comments[comment_index].replies.pop(reply_index)
            post.save()
    else:
        flash("Commenting is locked for this post.", category="error")
    comment_authors = get_comment_authors(post)
    return render_template(
        "blog/comments/comments.html",
        post=post,
        comment_authors=comment_authors,
        form=form,
        failed_comment_id=failed_comment_id,
        comment_error=comment_error,
    )


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

    next_page = form.next_page.data
    edit = False if post is None else True
    if edit is False:
        if post:
            flash("Post with that title already exists", category="error")
            return render_template("blog/create_post.html", form=form)
        post = BlogPost()

    post.title = form.title.data
    post.slug = get_slug(post.title)
    post.author = current_user.id
    post.published = form.publish.data
    post.can_comment = form.can_comment.data
    post.tags = list_from_string(form.tags.data, True)
    post.markdown_content = form.content.data.strip()
    post.html_content = markdown_to_html(post.markdown_content, table=True)
    post.markdown_description = form.description.data.strip()
    post.html_description = markdown_to_html(post.markdown_description)
    if edit is False:
        post.created_timestamp = datetime.now()
    post.updated_timestamp = datetime.now()
    post.save()

    if next_page:
        try:
            return redirect(url_for(f"blog.{next_page}", slug=post.slug))
        except Exception as e:
            print(f"got exception, e={e}")
    return redirect(url_for("blog.view", slug=post.slug))


def markdown_to_html(markdown_content, table=False):
    """Generate HTML representation of the markdown-formatted blog entry

    Also convert any media URLs into rich media objects such as video
    players or images.
    """
    hilite = CodeHiliteExtension(linenums=False, css_class="highlight")
    extras = ExtraExtension()
    toc = TocExtension(toc_depth=3)
    if table:
        markdown_content = "[TOC]\n\n" + markdown_content
    markdown_content = markdown(markdown_content, extensions=[hilite, extras, toc])
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
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = 0
    for post in posts:
        for tag in post.tags:
            tag_counts[tag] += 1
    # Sort by count after already sorted by tag
    tag_counts = OrderedDict(sorted(tag_counts.items(), key=lambda x: -x[1]))
    return tag_counts


def get_post_for_update_delete(slug):
    """Gets a post for update or delete and checks if it exists and is accessible"""
    # Slug is the True test of unique-ness
    post = BlogPost.objects(slug=slug).first()
    if not post:
        abort(404, "Blog post not found!")
    if post.author != current_user.id:
        abort(403, "Only blogpost author can edit post.")
    return post


def get_post_for_view(slug):
    """Gets a post for viewing and commenting"""
    post = BlogPost.objects(slug=slug).first()
    if not post:
        abort(404, "Blog post not found!")
    if post.published is False and (
        not current_user.is_authenticated or current_user.access_level != 1
    ):
        abort(
            401,
            "This post is unpublished. Only admin can view it, "
            "sorry. Check back later!",
        )
    return post


def get_comment_authors(post):
    """Gets authors of comments

    returns
        a dictionary like so:
            {
                user_id: user_object # with username, id, and avatar fields
            }
    """
    if post.comments:
        comment_author_ids = []
        for comment in post.comments:
            comment_author_ids.append(comment.author)
            if comment.replies:
                for reply in comment.replies:
                    comment_author_ids.append(reply.author)
        users = User.objects(id__in=comment_author_ids).only(
            "username", "avatar_location"
        )
        comment_authors = {user.id: user for user in users}

    else:
        comment_authors = {}
    return comment_authors


def sort_comments(comments):
    """Sort comments (or replies) from newest to oldest"""
    return sorted(comments, key=lambda comment: comment.created_timestamp, reverse=True)

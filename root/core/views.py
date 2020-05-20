from flask import Blueprint, render_template

from root.blog.views import query_and_paginate_blog

core = Blueprint("core", __name__)


@core.route("/")
def index():
    """This is the home page view"""
    blog_paginator = query_and_paginate_blog()
    return render_template("core/index.html", blog_paginator=blog_paginator)


@core.route("/info")
def info():
    """Info page view"""
    return render_template("core/info.html")

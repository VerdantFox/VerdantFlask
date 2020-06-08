"""Utility functions available throughout app"""
import re
from math import ceil


def setup_pagination(page, results_per_page, mongo_query):
    """Validate current page and create pagination object"""
    page = int(page)
    post_count = mongo_query.count()
    page_ceiling = ceil(post_count / results_per_page)
    if page > page_ceiling:
        page = page_ceiling
    elif page < 1:
        page = 1
    if post_count == 0:
        paginator = None
    else:
        paginator = mongo_query.paginate(page=page, per_page=results_per_page)
    return paginator


def get_slug(title):
    """Generate slug from title"""
    return re.sub(r"[^\w]+", "-", title.lower()).strip("-")


def list_from_string(string):
    """Generate a list from a string"""
    if not string:
        string = ""
    string_list = string.strip(" []()").split(",")
    return [item.strip().lower() for item in string_list]

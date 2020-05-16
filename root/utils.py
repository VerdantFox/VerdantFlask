"""Utility functions available throughout app"""
import os
from math import ceil

import yaml
from flask import redirect, request, url_for

# Secrets path
CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "secrets.yaml")
)


def get_secrets():
    """Gets a secrets file at the specified path and setting"""

    if not os.path.exists(CONFIG_PATH):
        raise EnvironmentError(f"secrets file not found at: {CONFIG_PATH}")
    with open(CONFIG_PATH) as conf:
        secrets = yaml.safe_load(conf)

    # debug = os.environ.get("DEBUG")
    debug = True
    if debug:
        secrets = extract_secret(secrets, "DEV")
    else:
        secrets = extract_secret(secrets, "PROD")

    return secrets


def extract_secret(secrets, secret):
    try:
        return secrets[secret]
    except KeyError as e:
        raise EnvironmentError(
            f"YAML not set up properly. Missing {e}. "
            "To run in debug mode use DEBUG=1"
        )


def set_environment_variables(variables):
    for var, val in variables.items():
        os.environ[var] = val


def redirect_next():
    """Redirect to page saved as 'next', else to the index"""
    next = request.args.get("next")
    if next is None or not next[0] == "/":
        next = url_for("core.index")
    return redirect(next)


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

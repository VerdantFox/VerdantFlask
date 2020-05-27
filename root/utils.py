"""Utility functions available throughout app"""
import os
import re
from math import ceil

import yaml

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

from flask import Blueprint, render_template
from flask_login import current_user

from . import budget

finance = Blueprint("finance", __name__)


@finance.route("/", methods=["GET"])
def landing() -> str:
    """The base page for the finance app"""
    return render_template("finance/landing.html")


@finance.route("/budget", methods=["GET"])
def budget_page() -> str:
    """Sub application for budget planning"""
    default_budget = budget.get_default_budget(current_user)
    return render_template(
        "finance/budget.html", budget=default_budget, id_safe=id_safe
    )


@finance.route("/budget/retrieve/{budget_id}", methods=["POST"])
def retrieve_budget(budget_id) -> str:
    """Retrieve a budget"""


@finance.route("/budget/share/{budget_id}", methods=["GET"])
def share_budget(budget_id) -> str:
    """Sub application for budget planning"""
    return render_template("finance/budget_share.html")


@finance.route("/stocks", methods=["GET"])
def stocks() -> str:
    """Sub application for stocks trading"""
    return render_template("finance/stocks.html")


@finance.route("/net_worth", methods=["GET"])
def net_worth() -> str:
    """Sub application for net worth calculating"""
    return render_template("finance/net_worth.html")


# ----------------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------------
def id_safe(phrase):
    """Make a DOM id HTML safe"""
    return phrase.replace(" ", "_").replace("&", "AND").strip()


def id_safe_reverse(phrase):
    """Make a safe DOM id HTML like the original"""
    return phrase.replace("_", " ").replace("AND", "&").strip()

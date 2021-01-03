import json

from flask import Blueprint, render_template, session
from flask_login import current_user, login_required

from . import budget
from .forms import BudgetForm
from .models import Budget

finance = Blueprint("finance", __name__)


@finance.route("/", methods=["GET"])
def landing() -> str:
    """The base page for the finance app"""
    return render_template("finance/landing.html")


# --------------------------------------------------------------------------
# Budget views
# --------------------------------------------------------------------------
@finance.route("/budget", methods=["GET"])
def budget_page() -> str:
    """Sub application for budget planning"""
    budget_json = session.get("current_budget")
    if budget_json:
        budget_dict = json.loads(budget_json)
        current_budget = Budget(**budget_dict)
    else:
        current_budget = budget.get_default_budget()
    form = BudgetForm()
    return render_template(
        "finance/budget.html", budget=current_budget, id_safe=id_safe, form=form
    )


@finance.route("/budget/new_budget", methods=["GET"])
def new_budget() -> str:
    """ Create a new budget, removing old one from stash """
    session.pop("current_budget", None)
    form = BudgetForm()
    return render_template(
        "finance/budget_inner.html",
        budget=budget.get_default_budget(),
        form=form,
        id_safe=id_safe,
        refresh_js=True,
    )


@finance.route("/budget/stash", methods=["POST"])
def stash_current_budget():
    """Stash the currently opened budget on the current_user object"""
    form = BudgetForm()
    if not form.validate_on_submit():
        print(dict(form.errors.items()))
        return dict(form.errors.items())
    stashed_budget = budget.set_budget_object(
        current_user,
        form.budget_json.data,
        form.budget_view_period.data,
        form.budget_name.data,
    )
    session["current_budget"] = stashed_budget.to_json()
    return {"cache": "success"}


@finance.route("/budget/save", methods=["POST"])
@login_required
def save_current_budget():
    """Save the currently opened budget to mongoengine"""


@finance.route("/budget/retrieve/{budget_id}", methods=["POST"])
@login_required
def retrieve_budget(budget_id) -> str:
    """Retrieve a budget, only available to budget owner"""


@finance.route("/budget/share/{budget_id}", methods=["GET"])
def share_budget(budget_id) -> str:
    """Retrieve a budget for sharing purposes, in uneditable format"""
    return render_template("finance/budget_share.html")


# --------------------------------------------------------------------------
# Stocks views
# --------------------------------------------------------------------------
@finance.route("/stocks", methods=["GET"])
def stocks() -> str:
    """Sub application for stocks trading"""
    return render_template("finance/stocks.html")


# --------------------------------------------------------------------------
# Net worth views
# --------------------------------------------------------------------------
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

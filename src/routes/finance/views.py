from typing import Union

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from . import budget_helpers
from .forms import BudgetForm

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
    return render_template(
        "finance/budget.html",
        budget=budget_helpers.get_current_or_default_budget(),
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        id_safe=id_safe,
        form=BudgetForm(),
    )


@finance.route("/budget/new_budget", methods=["GET"])
def new_budget() -> str:
    """ Create a new budget, removing old one from stash """
    budget_helpers.save_budget()
    session.pop("current_budget", None)
    form = BudgetForm()
    return render_template(
        "finance/budget_inner.html",
        budget=budget_helpers.get_default_budget(),
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        id_safe=id_safe,
        refresh_js=True,
    )


@finance.route("/budget/stash", methods=["POST"])
def stash_current_budget():
    """Stash the currently opened budget in the session"""
    stashed_budget = budget_helpers.set_budget_from_post()
    session["current_budget"] = stashed_budget.to_json()
    return {"budget_stash": "success"}


@finance.route("/budget/save", methods=["POST"])
@login_required
def save_current_budget():
    """Save the currently opened budget to mongoengine"""
    form = BudgetForm()
    budget_obj = budget_helpers.save_budget()
    return render_template(
        "finance/budget_inner.html",
        budget=budget_obj,
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        id_safe=id_safe,
        refresh_js=True,
    )


@finance.route("/budget/retrieve/<budget_id>", methods=["POST"])
@login_required
def retrieve_budget(budget_id) -> str:
    """Retrieve a budget, only available to budget owner"""
    form = BudgetForm()
    budget_helpers.save_budget()
    return render_template(
        "finance/budget_inner.html",
        budget=budget_helpers.retrieve_budget(budget_id),
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        id_safe=id_safe,
        refresh_js=True,
    )


@finance.route("/budget/delete/<budget_id>", methods=["POST"])
@login_required
def delete_budget(budget_id) -> str:
    """Retrieve a budget, only available to budget owner"""
    form = BudgetForm()
    if budget_id == form.budget_id.data:
        session.pop("current_budget", None)
    else:
        budget_helpers.save_budget()
    budget_helpers.delete_budget(budget_id)
    return render_template(
        "finance/budget_inner.html",
        budget=budget_helpers.get_current_or_default_budget(),
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        id_safe=id_safe,
        refresh_js=True,
    )


@finance.route("/budget/share/<budget_id>", methods=["GET", "POST"])
def share_budget(budget_id) -> Union[str, Response]:
    """Retrieve a budget for sharing purposes, in uneditable format"""
    if request.method == "POST":
        budget_helpers.save_budget()
        return redirect(url_for("finance.share_budget", budget_id=budget_id))
    return render_template(
        "finance/budget_share.html",
        budget=budget_helpers.retrieve_budget(budget_id),
        is_share=True,
    )


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

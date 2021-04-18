from typing import Union

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from . import budget_graphs, budget_helpers
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
    budget = budget_helpers.get_current_or_default_budget()
    return render_template(
        "finance/budget.html",
        budget=budget,
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=BudgetForm(),
        graphs=budget_graphs.prepare_all_budget_graphs(budget),
    )


@finance.route("/budget/update", methods=["POST"])
def update_current_budget() -> str:
    """Stash the currently opened budget in the session and return graphs"""
    budget = budget_helpers.set_budget_from_post()
    session["current_budget"] = budget.to_json()
    return budget_graphs.prepare_all_budget_graphs(budget)


@finance.route("/budget/new", methods=["GET"])
def new_budget() -> str:
    """Create a new budget, removing old one from stash"""
    budget_helpers.save_budget()
    session.pop("current_budget", None)
    form = BudgetForm()
    budget = budget_helpers.get_default_budget()
    return render_template(
        "finance/budget_inner.html",
        budget=budget,
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        refresh_js=True,
        graphs=None,
    )


@login_required
@finance.route("/budget/copy", methods=["POST"])
def copy_budget() -> str:
    """Copy the current budget"""
    budget_helpers.save_budget()
    form = BudgetForm()
    budget = budget_helpers.copy_current_budget()
    session["current_budget"] = budget.to_json()
    return render_template(
        "finance/budget_inner.html",
        budget=budget,
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        refresh_js=True,
        graphs=budget_graphs.prepare_all_budget_graphs(budget),
    )


@finance.route("/budget/save", methods=["POST"])
@login_required
def save_current_budget() -> str:
    """Save the currently opened budget to mongoengine"""
    form = BudgetForm()
    budget = budget_helpers.save_budget()
    session["current_budget"] = budget.to_json()
    return render_template(
        "finance/budget_inner.html",
        budget=budget,
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        refresh_js=True,
    )


@finance.route("/budget/retrieve/<budget_id>", methods=["POST"])
@login_required
def retrieve_budget(budget_id: str) -> str:
    """Retrieve a budget, only available to budget owner"""
    form = BudgetForm()
    budget_helpers.save_budget()
    budget = budget_helpers.retrieve_budget(budget_id)
    session["current_budget"] = budget.to_json()
    return render_template(
        "finance/budget_inner.html",
        budget=budget,
        saved_budgets=budget_helpers.get_user_budgets_limited(),
        form=form,
        refresh_js=True,
        graphs=budget_graphs.prepare_all_budget_graphs(budget),
    )


@finance.route("/budget/delete/<budget_id>", methods=["POST"])
@login_required
def delete_budget(budget_id: str) -> str:
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
        refresh_js=True,
    )


@finance.route("/budget/share/<budget_id>", methods=["GET", "POST"])
def share_budget(budget_id: str) -> Union[str, Response]:
    """Retrieve a budget for sharing purposes, in uneditable format"""
    if request.method == "POST":
        budget_helpers.save_budget()
        return redirect(url_for("finance.share_budget", budget_id=budget_id))
    budget = budget_helpers.retrieve_budget(budget_id)
    return render_template(
        "finance/budget_share.html",
        budget=budget,
        is_share=True,
        graphs=budget_graphs.prepare_all_budget_graphs(budget),
    )


# --------------------------------------------------------------------------
# Loan views
# --------------------------------------------------------------------------
@finance.route("/loan", methods=["GET"])
def loan() -> str:
    """Sub application for loan calculating"""
    return render_template("finance/loan.html")


# --------------------------------------------------------------------------
# Compound Interest views
# --------------------------------------------------------------------------
@finance.route("/compound_interest", methods=["GET"])
def compound_interest() -> str:
    """Sub application for compound interest calculating"""
    return render_template("finance/compound_interest.html")


# --------------------------------------------------------------------------
# Net worth views
# --------------------------------------------------------------------------
@finance.route("/net_worth", methods=["GET"])
def net_worth() -> str:
    """Sub application for net worth calculating"""
    return render_template("finance/net_worth.html")


# --------------------------------------------------------------------------
# Stocks views
# --------------------------------------------------------------------------
@finance.route("/stocks", methods=["GET"])
def stocks() -> str:
    """Sub application for stocks trading"""
    return render_template("finance/stocks.html")

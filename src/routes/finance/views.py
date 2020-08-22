from flask import Blueprint, render_template

finance = Blueprint("finance", __name__)


@finance.route("/", methods=["GET"])
def landing() -> str:
    """The base page for the finance app"""
    return render_template("finance/landing.html")


@finance.route("/budget", methods=["GET"])
def budget() -> str:
    """Sub application for budget planning"""
    return render_template("finance/budget.html")


@finance.route("/stocks", methods=["GET"])
def stocks() -> str:
    """Sub application for stocks trading"""
    return render_template("finance/stocks.html")


@finance.route("/net_worth", methods=["GET"])
def net_worth() -> str:
    """Sub application for net worth calculating"""
    return render_template("finance/net_worth.html")

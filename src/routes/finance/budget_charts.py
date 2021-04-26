"""budget_graphs:  produce bokeh graphs for budget"""
from flask import url_for

from .budget_helpers import TIME_PERIOD_CONVERTER
from .charts_common import combine_charts, produce_bar_chart, produce_pie_chart
from .models import Budget


def prepare_budget_categories_data(budget: Budget) -> dict[str, int]:
    """Prepare the categories data for graphing"""
    view_period = budget.period
    category_data = {}
    for category in budget.budget:
        category_data[category] = 0
        for item in budget.budget[category]:
            positive = budget.budget[category][item]["pos"]
            if positive:
                continue
            value = budget.budget[category][item]["value"]
            if not value:
                continue
            period = budget.budget[category][item]["period"]
            category_data[category] += value * period // view_period
    data_copy = category_data.copy()
    for cat, val in data_copy.items():
        if val == 0:
            category_data.pop(cat)
    return category_data


def prepare_budget_items_data(budget: Budget, income: bool = False) -> dict[str, int]:
    """Prepare items data for graphing"""
    view_period = budget.period
    item_data: dict[str, int] = {}
    total = 0
    for category in budget.budget:
        for item in budget.budget[category]:
            positive = budget.budget[category][item]["pos"]
            if positive and not income:
                continue
            if not positive and income:
                continue
            value = budget.budget[category][item]["value"]
            if not value:
                continue
            period = budget.budget[category][item]["period"]
            relative_value = value * period // view_period
            if item_data.get(item):
                item_data[f"{item} ({category})"] = relative_value
            else:
                item_data[item] = relative_value
            total += relative_value
    if total == 0:
        return {}
    data_copy = item_data.copy()
    other = "Other items (<2% of total)"
    item_data[other] = 0
    for item, val in data_copy.items():
        rel_freq = val / total
        if rel_freq < 0.02:
            item_data[other] += val
            item_data.pop(item)
    if not item_data.get(other):
        item_data.pop(other)
    return item_data


def prepare_income_vs_expenses_data(budget: Budget) -> dict[str, int]:
    """Prepare data for income vs expenses"""
    view_period = budget.period
    ive_data = {"Income": 0, "Expenses": 0}
    for category in budget.budget:
        for item in budget.budget[category]:
            positive = budget.budget[category][item]["pos"]
            value = budget.budget[category][item]["value"]
            if not value:
                continue
            period = budget.budget[category][item]["period"]
            if positive:
                ive_data["Income"] += value * period // view_period
            else:
                ive_data["Expenses"] += value * period // view_period
    return ive_data


def inject_advice(positive: bool):
    """Inject an advice section above charts"""
    advice_str = "<br><div class='container advice'><p>"
    if positive:
        advice_str += """It looks like your income is greater than your spending.
Congratulations, that's great! Can we do even better? """
    else:
        advice_str += """It looks like your spending is greater than your income.
Maybe there is room for improvement. """
    advice_str += """Take a look at the charts above. Are there any major expenses
you can find that can be reduced or eliminated? Examine your income. Are you satisfied
with where it's at, or are you looking to improve it, maybe through a new or extra
job or increased hours?"""
    if positive:
        advice_str += "</p><p>What can you do with your budget surplus? "
    else:
        advice_str += (
            "</p><p>What are your options once your budget is back in the black? "
        )
    advice_str += f"""Consider paying down loans, investing (or investing more) in retirement
accounts, or saving for an important purchase or rainy day fund. If you are interested in
investing and growing your net worth, check out the
<a href="{url_for('finance.stocks')}">stocks</a> and
<a href="{url_for('finance.net_worth')}">net worth</a> pages.</p></div>"""
    return advice_str


def prepare_all_budget_charts(budget: Budget) -> str:
    """Prepare all budget graphs"""
    view_period = budget.period
    categories_data = prepare_budget_categories_data(budget)
    items_data = prepare_budget_items_data(budget)
    income_data = prepare_budget_items_data(budget, income=True)
    income_v_expense_data = prepare_income_vs_expenses_data(budget)
    if all((categories_data, items_data, income_data, income_v_expense_data)):
        categories_chart = produce_pie_chart(
            categories_data,
            f"Budget Spent by Category ({TIME_PERIOD_CONVERTER[view_period]})",
        )
        items_chart = produce_pie_chart(
            items_data,
            f"Budget Spent by Item ({TIME_PERIOD_CONVERTER[view_period]})",
        )
        income_chart = produce_pie_chart(
            income_data,
            f"Income by Item ({TIME_PERIOD_CONVERTER[view_period]})",
        )
        ive_chart = produce_bar_chart(
            income_v_expense_data,
            f"Income vs Expenses ({TIME_PERIOD_CONVERTER[view_period]})",
            colors=["#003300", "#7f1a22"],
        )
        positive = income_v_expense_data["Income"] > income_v_expense_data["Expenses"]
        combined_charts = combine_charts(
            categories_chart, items_chart, income_chart, ive_chart
        )
        return combined_charts + inject_advice(positive)
    else:
        return "<h2>Graphs unavailable</h2>"

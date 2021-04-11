"""budget_graphs:  produce bokeh graphs for budget"""
from math import pi

import pandas as pd
from bokeh.embed import components
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.palettes import Viridis6, viridis
from bokeh.plotting import figure
from bokeh.transform import cumsum

from .budget_helpers import TIME_PERIOD_CONVERTER


def prepare_budget_categories_data(budget):
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


def prepare_budget_items_data(budget, income=False):
    """Prepare items data for graphing"""
    view_period = budget.period
    item_data = {}
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


def prepare_income_vs_expenses_data(budget):
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


def produce_pie_chart(data_dict, descriptor, title):
    """Produce a pie chart div, given data"""
    data = (
        pd.Series(data_dict)
        .reset_index(name="value")
        .rename(columns={"index": descriptor})
    )
    data["angle"] = data["value"] / data["value"].sum() * 2 * pi
    data["color"] = viridis(len(data_dict))
    data["percentage"] = round(data["value"] / data["value"].sum() * 100)

    plot = figure(
        sizing_mode="scale_width",
        title=title,
        toolbar_location=None,
        tools="hover",
        tooltips=f"@{descriptor}: $@value{{,}} (@percentage%)",
        x_range=(-0.5, 1.0),
    )

    plot.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        legend_field=descriptor,
        source=data,
    )

    # Adjust plot settings
    plot.axis.axis_label = None
    plot.axis.visible = False
    plot.grid.grid_line_color = None
    plot.title.text_font_size = "1.25rem"
    plot.border_fill_alpha = 0
    plot.background_fill_alpha = 0
    plot.legend.border_line_alpha = 0
    plot.legend.background_fill_alpha = 0.5

    script, div = components(plot)
    return script, div


def produce_bar_chart(data_dict, descriptor, title):
    """Produce a bar chart"""
    x = list(data_dict.keys())
    dollars = list(data_dict.values())
    colors = ["#09A029", "#9B0C0C"] if len(x) == 2 else Viridis6
    source = ColumnDataSource(data=dict(x=x, dollars=dollars, color=colors))
    plot = figure(
        sizing_mode="scale_width",
        title=title,
        toolbar_location=None,
        tools="hover",
        tooltips=f"@{descriptor}: $@dollars{{,}}",
        x_range=x,
    )
    plot.vbar(
        x="x",
        top="dollars",
        width=0.9,
        source=source,
        line_color="white",
        color="color",
    )

    # Adjust plot settings
    plot.yaxis[0].formatter = NumeralTickFormatter(format="$0,0")
    plot.title.text_font_size = "1.2rem"
    plot.axis.major_label_text_font_size = "1rem"
    plot.border_fill_alpha = 0
    plot.background_fill_alpha = 0
    plot.background_fill_alpha = 0
    plot.xgrid.visible = False
    plot.ygrid.visible = False

    script, div = components(plot)
    return script, div


def combine_charts(*charts):
    """Combine all chart data"""
    html = '<div class="row">'
    for i, (script, div) in enumerate(charts, start=1):
        if i % 2 == 1 and i != 1:
            html += '<div class="row">'
        html += f'<div class="col-lg-6">{script}{div}</div>'
        if i % 2 == 0 or i == len(charts):
            html += "</div>"
    return html


def prepare_all_budget_graphs(budget):
    """Prepare all budget graphs"""
    view_period = budget.period
    categories_data = prepare_budget_categories_data(budget)
    items_data = prepare_budget_items_data(budget)
    income_data = prepare_budget_items_data(budget, income=True)
    income_v_expense_data = prepare_income_vs_expenses_data(budget)
    if all((categories_data, items_data, income_data, income_v_expense_data)):
        categories_script, categories_div = produce_pie_chart(
            categories_data,
            "Category",
            f"Budget Spent by Category ({TIME_PERIOD_CONVERTER[view_period]})",
        )
        items_script, items_div = produce_pie_chart(
            items_data,
            "Item",
            f"Budget Spent by Item ({TIME_PERIOD_CONVERTER[view_period]})",
        )
        income_script, income_div = produce_pie_chart(
            income_data,
            "Item",
            f"Income by Item ({TIME_PERIOD_CONVERTER[view_period]})",
        )
        ive_script, ive_div = produce_bar_chart(
            income_v_expense_data,
            "x",
            f"Income vs Expenses ({TIME_PERIOD_CONVERTER[view_period]})",
        )
        return combine_charts(
            (categories_script, categories_div),
            (items_script, items_div),
            (income_script, income_div),
            (ive_script, ive_div),
        )
    else:
        return "<h2>Graphs unavailable</h2>"

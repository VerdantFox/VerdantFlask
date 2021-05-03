"""loan_graphs: bokeh graphs for loans"""
from typing import Any

from dateutil.relativedelta import relativedelta

from .charts_common import (
    combine_charts,
    produce_line_chart,
    produce_pie_chart,
    produce_stacked_bar_chart,
    produce_stacked_line_chart,
)


def prepare_loan_amortization(calc) -> dict[str, dict[str, Any]]:
    """Prepare amortization data for graphing"""
    chart_data = {
        # For pie chart
        "pie": {
            "Principal": calc.principal,
            "Interest": calc.total_interest,
        },
        # For per year chart
        "per year": {
            "Years": calc.years,
            "Principal": calc.principal_per_year,
            "Interest": calc.interest_per_year,
            "Payment": calc.payment_per_year,
        },
        # For per period payment chart
        "per period": {
            "Payment date": [],
            # "Payment": [],
            "Interest": [],
            "Principal": [],
        },
        # For loan amortization chart
        "amortization": {
            "Payment date": [calc.start_date - relativedelta(months=1)],
            "Principal paid": [0],
            "Interst paid": [0],
            "Balance remaining": [calc.principal],
        },
    }
    for (
        date,
        payment,
        principal,
        interest,
        tot_interest,
        balance,
    ) in calc.amortization_schedule:
        # For per period payment chart
        chart_data["per period"]["Payment date"].append(date)
        # chart_data["per period"]["Payment"].append(payment)
        chart_data["per period"]["Principal"].append(principal)
        chart_data["per period"]["Interest"].append(interest)
        # For loan amortization chart
        chart_data["amortization"]["Payment date"].append(date)
        chart_data["amortization"]["Principal paid"].append(
            calc.round_money(calc.principal - balance)
        )
        chart_data["amortization"]["Interst paid"].append(tot_interest)
        chart_data["amortization"]["Balance remaining"].append(balance)
    return chart_data


def produce_loan_graphs(calc):
    """Produce all loan graphs"""
    chart_data = prepare_loan_amortization(calc)
    pie_chart = produce_pie_chart(
        data_dict=chart_data["pie"],
        title="Percentage of total loan cost",
        colors=["#261fab", "#a8222d"],
    )
    amo_chart = produce_line_chart(
        x_val=chart_data["amortization"].pop("Payment date"),
        y_vals=chart_data["amortization"].items(),
        title="Totals over time",
        colors=["#261fab", "#a8222d", "#006622"],
    )
    per_period_stack_chart = produce_stacked_line_chart(
        x_val=chart_data["per period"].pop("Payment date"),
        y_vals=chart_data["per period"].items(),
        title="Payments over time",
        colors=["#a8222d", "#261fab"],
    )
    per_year_chart = produce_stacked_bar_chart(
        data=chart_data["per year"],
        x_label="Years",
        legend_labels=["Interest", "Principal"],
        title="Amount paid per year",
        colors=["#a8222d", "#261fab"],
    )

    return combine_charts(pie_chart, per_year_chart, per_period_stack_chart, amo_chart)

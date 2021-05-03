"""forms: forms related to finance"""
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import request
from flask_wtf import FlaskForm
from wtforms import (
    DateTimeField,
    FloatField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.validators import Length, NumberRange

VIEW_PERIODS = {
    52: "Weekly",
    26: "Fortnightly",
    24: "bimonthly",
    12: "Monthly",
    4: "Quarterly",
    2: "Biannually",
    1: "Annually",
}


class BudgetForm(FlaskForm):
    budget_id = HiddenField("Budget ID")
    budget_name = StringField(
        "Budget Name", description="My First Budget", validators=[Length(max=30)]
    )
    budget_view_period = SelectField(
        "View Time Period", choices=[(key, val) for key, val in VIEW_PERIODS.items()]
    )
    budget_json = HiddenField("Budget")


MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}
TODAY = datetime.today()
TOMORROW = TODAY + relativedelta(days=1)
NEXT_MONTH = (TODAY + relativedelta(months=1)).month

LOAN_PERIODS = [(12, "Years"), (1, "Months")]


class LoanForm(FlaskForm):
    principal = FloatField(
        "Loan amount", validators=[NumberRange(min=0)], default=5_000
    )
    interest_rate = FloatField(
        "Interest rate per year", validators=[NumberRange(min=0)], default=4.5
    )
    period = IntegerField(
        "Loan period", validators=[NumberRange(min=0, max=600)], default=5
    )
    period_type = SelectField("In terms of", choices=LOAN_PERIODS, default=12)
    extra_monthly = FloatField(
        "Extra monthly payment", validators=[NumberRange(min=0)], default=0
    )
    extra_yearly = FloatField(
        "Extra Yearly payment", validators=[NumberRange(min=0)], default=0
    )
    extra_yearly_month = SelectField(
        "Occuring every",
        choices=[(key, val) for key, val in MONTHS.items()],
        default=NEXT_MONTH,
    )
    start_date = DateTimeField("Start date", format="%Y-%m-%d", default=(TOMORROW))


COMOUND_PERIODS = {
    365: "Daily",
    52: "Weekly",
    12: "Monthly",
    4: "Quarterly",
    2: "Biannually",
    1: "Annually",
}


class InterestForm(FlaskForm):
    initial = FloatField(
        "Initial investment", validators=[NumberRange(min=0)], default=5_000
    )
    nbr_of_years = IntegerField(
        "Number of years", validators=[NumberRange(min=0, max=100)], default=10
    )
    apy = FloatField("Estimated APY", validators=[NumberRange(min=0)], default=8.0)
    compounding_period = SelectField(
        "Compounding",
        choices=[(key, val) for key, val in COMOUND_PERIODS.items()],
        default=365,
    )
    apy_variance = FloatField(
        "APY variance", validators=[NumberRange(min=0)], default=3.0
    )
    contributions = SelectField(
        "Contributions",
        choices=[("Deposits", "Deposits"), ("Withdrawls", "Withdrawls")],
        default="Deposits",
    )
    monthly = FloatField("Monthly", validators=[NumberRange(min=0)], default=0)
    yearly = FloatField("Yearly", validators=[NumberRange(min=0)], default=0)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
class ArgConverter:
    """Convert request args for form GET requests"""

    def __init__(self):
        """Initialize values"""
        self.args = {}

    def convert_dict(self, dictionary):
        """Convert all values from conversion dictionary"""
        for key, conversion in dictionary.items():
            self.convert(key, conversion)

    def convert(self, key, conversion):
        """Convert request dict item"""
        value = request.args.get(key)
        if value is None:
            return
        try:
            self.args[key] = conversion(value)
        except (TypeError, ValueError):
            pass


def convert_dt(value):
    """Convert a datetime value"""
    return datetime.strptime(value, "%Y-%m-%d")


def convert_and_populate_form(form, conversion_dict):
    """Convert form values and populate form"""
    arg_converter = ArgConverter()
    arg_converter.convert_dict(conversion_dict)
    return form(meta={"csrf": False}, **arg_converter.args)

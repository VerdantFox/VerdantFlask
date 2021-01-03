"""forms: forms related to finance"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField
from wtforms.validators import Length

VIEW_PERIODS = [
    (52, "Weekly"),
    (26, "Fortnightly"),
    (24, "bimonthly"),
    (12, "Monthly"),
    (4, "Quarterly"),
    (2, "Biannually"),
    (1, "Annually"),
]


class BudgetForm(FlaskForm):
    budget_name = StringField(
        "Budget Name", description="My First Budget", validators=[Length(max=30)]
    )
    budget_view_period = SelectField("View Time Period", choices=VIEW_PERIODS)
    budget_json = HiddenField("Budget")

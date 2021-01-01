"""forms: forms related to finance"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class BudgetForm(FlaskForm):
    budget_name = StringField(
        "Budget Name", description="My First Budget", validators=[DataRequired()]
    )
    budget_view = SelectField("View Time Period")
    budget_json = HiddenField("Budget")
    submit_budget = SubmitField("Save Budget")

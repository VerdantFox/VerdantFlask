"""budget: module for handling budget.py logic"""
import json
from copy import deepcopy
from typing import List, Optional

from bson.objectid import ObjectId
from flask import session
from flask_login import current_user

from .forms import BudgetForm
from .models import Budget

TIME_PERIOD_CONVERTER = {
    52: "Weekly",
    26: "Fortnightly",
    24: "Bimonthly",
    12: "Monthly",
    4: "Quarterly",
    2: "Biannually",
    1: "Annually",
}
DEFAULT_FIELD_POS = {"value": None, "period": 12, "pos": True}
DEFAULT_FIELD_NEG = {"value": None, "period": 12, "pos": False}
DEFAULT_BUDGET = {
    "Income": {
        "Your wages/salary": DEFAULT_FIELD_POS,
        "Partner's wages/salary": DEFAULT_FIELD_POS,
        "Tips": DEFAULT_FIELD_POS,
        "Bonuses & overtime": DEFAULT_FIELD_POS,
        "Income from investments": DEFAULT_FIELD_POS,
        "Child support recieved": DEFAULT_FIELD_POS,
        "Stipend": DEFAULT_FIELD_POS,
    },
    "Home & Utilities": {
        "Mortgage or Rent": DEFAULT_FIELD_NEG,
        "HOA": DEFAULT_FIELD_NEG,
        "Furniture & appliances": DEFAULT_FIELD_NEG,
        "Renovations & Maintenance": DEFAULT_FIELD_NEG,
        "Electricity": DEFAULT_FIELD_NEG,
        "Gas": DEFAULT_FIELD_NEG,
        "Water": DEFAULT_FIELD_NEG,
        "Internet": DEFAULT_FIELD_NEG,
        "TV & Streaming": DEFAULT_FIELD_NEG,
        "Phone bill(s)": DEFAULT_FIELD_NEG,
    },
    "Insurance & Financial": {
        "Income taxes": DEFAULT_FIELD_NEG,
        "Other taxes": DEFAULT_FIELD_NEG,
        "Car insurance": DEFAULT_FIELD_NEG,
        "Home insurance": DEFAULT_FIELD_NEG,
        "Personal & life insurance": DEFAULT_FIELD_NEG,
        "Health insurance": DEFAULT_FIELD_NEG,
        "Car loan": DEFAULT_FIELD_NEG,
        "Student loan": DEFAULT_FIELD_NEG,
        "Credit card interest": DEFAULT_FIELD_NEG,
        "Other loans": DEFAULT_FIELD_NEG,
        "Paying off debt": DEFAULT_FIELD_NEG,
        "Savings": DEFAULT_FIELD_NEG,
        "401K / retirement account": DEFAULT_FIELD_NEG,
        "Retirement individual contribution": DEFAULT_FIELD_NEG,
        "Property investments": DEFAULT_FIELD_NEG,
        "Other investments": DEFAULT_FIELD_NEG,
        "Donations & Charity": DEFAULT_FIELD_NEG,
    },
    "Food & Groceries": {
        "Supermarket": DEFAULT_FIELD_NEG,
        "Pet food/expenses": DEFAULT_FIELD_NEG,
        "Lunches - bought": DEFAULT_FIELD_NEG,
        "Restaurants": DEFAULT_FIELD_NEG,
        "Snacks": DEFAULT_FIELD_NEG,
        "Cigarettes & similar": DEFAULT_FIELD_NEG,
        "Coffee & Tea": DEFAULT_FIELD_NEG,
        "Drinks & alcohol": DEFAULT_FIELD_NEG,
        "Bars & Clubs": DEFAULT_FIELD_NEG,
    },
    "Medical & Personal Care": {
        "Pet & vet care": DEFAULT_FIELD_NEG,
        "Doctors visits": DEFAULT_FIELD_NEG,
        "Surgery/procdures": DEFAULT_FIELD_NEG,
        "Perscriptions": DEFAULT_FIELD_NEG,
        "Glasses & eye care": DEFAULT_FIELD_NEG,
        "Dental": DEFAULT_FIELD_NEG,
        "Cosmetics & toiletries": DEFAULT_FIELD_NEG,
        "Hair & Beauty": DEFAULT_FIELD_NEG,
        "Gym": DEFAULT_FIELD_NEG,
        "Education expenses": DEFAULT_FIELD_NEG,
        "Clothing & shoes": DEFAULT_FIELD_NEG,
        "Jewelry & accessories": DEFAULT_FIELD_NEG,
    },
    "Entertainment & Hobbies": {
        "Books": DEFAULT_FIELD_NEG,
        "Newspaper & Magazine": DEFAULT_FIELD_NEG,
        "Movies": DEFAULT_FIELD_NEG,
        "Video games": DEFAULT_FIELD_NEG,
        "Computer & gadgets": DEFAULT_FIELD_NEG,
        "Sports": DEFAULT_FIELD_NEG,
        "Hobbies": DEFAULT_FIELD_NEG,
        "Vacations": DEFAULT_FIELD_NEG,
        "Celebrations & gifts": DEFAULT_FIELD_NEG,
    },
    "Transportation & Auto": {
        "Bus/train/ferry": DEFAULT_FIELD_NEG,
        "Gas": DEFAULT_FIELD_NEG,
        "Road tolls & parking": DEFAULT_FIELD_NEG,
        "Registration & smog": DEFAULT_FIELD_NEG,
        "Repairs & maintenance": DEFAULT_FIELD_NEG,
        "Fines": DEFAULT_FIELD_NEG,
        "Airfares": DEFAULT_FIELD_NEG,
        "Hotel & accommodations": DEFAULT_FIELD_NEG,
    },
    "Children": {
        "Prenatal": DEFAULT_FIELD_NEG,
        "Medical": DEFAULT_FIELD_NEG,
        "Dental": DEFAULT_FIELD_NEG,
        "Therapy": DEFAULT_FIELD_NEG,
        "Baby products": DEFAULT_FIELD_NEG,
        "Books & Toys": DEFAULT_FIELD_NEG,
        "Babysitting": DEFAULT_FIELD_NEG,
        "Childcare": DEFAULT_FIELD_NEG,
        "Sports & activities": DEFAULT_FIELD_NEG,
        "School tutition": DEFAULT_FIELD_NEG,
        "School fees": DEFAULT_FIELD_NEG,
        "School supplies": DEFAULT_FIELD_NEG,
        "School lunches": DEFAULT_FIELD_NEG,
        "Other school needs": DEFAULT_FIELD_NEG,
        "Excursions": DEFAULT_FIELD_NEG,
        "Allowance": DEFAULT_FIELD_NEG,
        "Child support payment": DEFAULT_FIELD_NEG,
        "College fund": DEFAULT_FIELD_NEG,
    },
}


def json_to_obj(budget_json: str) -> Budget:
    """Deserialize a budget json to a budget object"""
    budget_dict = json.loads(budget_json)
    author = budget_dict.pop("author", None)
    if author:
        budget_dict["author"] = ObjectId(author["$oid"])
    budget_dict["id"] = ObjectId(budget_dict.pop("_id")["$oid"])
    return Budget(**budget_dict)


def get_default_budget() -> Budget:
    """Get the default budget as a mongodb Budget model"""
    return Budget(budget=DEFAULT_BUDGET)


def get_current_or_default_budget() -> Budget:
    """Retrieve current budget from session or default budget if none in session"""
    budget_json = session.get("current_budget")
    if budget_json:
        return json_to_obj(budget_json)
    return get_default_budget()


def set_budget_object(
    budget_json: Optional[str],
    period: int = 12,
    budget_name: Optional[str] = None,
    budget_id: Optional[str] = None,
):
    """Return an instantiated Budget object"""
    if isinstance(budget_json, str):
        budget_json = json.loads(budget_json.strip())
    budget = Budget(budget=budget_json, period=period)
    try:
        budget.author = current_user.id
    except AttributeError:
        pass
    if budget_id:
        budget.id = ObjectId(budget_id)
    if budget_name:
        budget.name = budget_name
    return budget


def set_budget_from_post() -> Budget:
    """Set a budget object from form post"""
    form = BudgetForm()
    if not form.validate_on_submit():
        raise RuntimeError(dict(form.errors.items()))
    return set_budget_object(
        form.budget_json.data,
        form.budget_view_period.data,
        form.budget_name.data,
        form.budget_id.data,
    )


def copy_current_budget() -> Budget:
    """Copy the current budget"""
    budget = get_current_or_default_budget()
    budget_copy = deepcopy(budget)
    budget_copy.id = None
    budget_name = budget.name or "unnamed_budget"
    if not budget_name.endswith(" (copy)"):
        budget_name += " (copy)"
    budget_copy.name = budget_name
    budget_copy.save()
    return budget_copy


def get_user_budgets_limited() -> List[Budget]:
    """Get the saved budget names of the current user"""
    if current_user.is_authenticated:
        return Budget.objects(author=current_user.id).only("name")
    return []


def budget_is_default(budget_obj: Budget) -> bool:
    """A test to see if the budget is equivalent to the default budget"""
    default = json.loads(get_default_budget().to_json())
    incoming = json.loads(budget_obj.to_json())
    for budget_dict in (default, incoming):
        budget_dict.pop("_id", None)
        budget_dict.pop("author", None)
    return bool(default == incoming)


def save_budget() -> Budget:
    """Save current budget"""
    if not current_user.is_authenticated:
        return get_current_or_default_budget()
    try:
        budget_obj = set_budget_from_post()
    except RuntimeError:
        budget_obj = get_current_or_default_budget()
    if budget_is_default(budget_obj):
        return budget_obj
    if not budget_obj.name:
        budget_obj.name = "unnamed budget"
    budget_obj.save()
    return budget_obj


def retrieve_budget(budget_id: str) -> Budget:
    """Retrieve a specific saved budget"""
    return Budget.objects(id=budget_id).first()


def delete_budget(budget_id: str) -> Budget:
    """Delete a specific saved budget"""
    return Budget.objects(id=budget_id).first().delete()

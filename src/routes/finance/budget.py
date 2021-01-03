"""budget: module for handling budget.py logic"""
import json

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
DEFAULT_FIELD_NEG = {"value": None, "period": 12}
DEFAULT_BUDGET = {
    "Income": {
        "Your take-home pay": DEFAULT_FIELD_POS,
        "Partner's take-home pay": DEFAULT_FIELD_POS,
        "Bonuses & overtime": DEFAULT_FIELD_POS,
        "Income from investments": DEFAULT_FIELD_POS,
        "Child support recieved": DEFAULT_FIELD_POS,
        "Stipend": DEFAULT_FIELD_POS,
        "Other": DEFAULT_FIELD_POS,
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
        "Other": DEFAULT_FIELD_NEG,
    },
    "Insurance & Financial": {
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
        "Property investments": DEFAULT_FIELD_NEG,
        "Other investments": DEFAULT_FIELD_NEG,
        "Donations & Charity": DEFAULT_FIELD_NEG,
        "Other": DEFAULT_FIELD_NEG,
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
        "Other": DEFAULT_FIELD_NEG,
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
        "Other": DEFAULT_FIELD_NEG,
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
        "Other": DEFAULT_FIELD_NEG,
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
        "Other": DEFAULT_FIELD_NEG,
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
        "Other": DEFAULT_FIELD_NEG,
    },
}


def get_default_budget():
    """Get the default budget as a mongodb Budget model"""
    return Budget(budget=DEFAULT_BUDGET)


def set_budget_object(
    current_user,
    budget_json,
    period=12,
    budget_name=None,
    budget_id=None,
    budget_period=None,
):
    """Return an instantiated Budget object"""
    if isinstance(budget_json, str):
        budget_json = json.loads(budget_json)
    budget = Budget(budget=budget_json, period=period)
    try:
        budget.author = current_user.id
    except AttributeError:
        pass
    if budget_id:
        budget.id = budget_id
    if budget_name:
        budget.name = budget_name
    return budget


def save_budget():
    """Save a budget"""
    pass


def delete_budget():
    """Delete a budget"""
    pass

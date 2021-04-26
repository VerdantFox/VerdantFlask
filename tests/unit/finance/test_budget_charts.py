"""test_budget_charts: test the finance.budget_charts.py functions not hit by functional tests"""
import pytest
from bson.objectid import ObjectId

from src.routes.finance import budget_charts
from src.routes.finance.models import Budget

BUDGET_VARIED = {
    "category_pos": {"item1": {"value": 100, "period": 12, "pos": True}},
    "category_neg1": {
        "item_lg": {"value": 1000, "period": 12, "pos": False},
        "item_sm": {"value": 100, "period": 1, "pos": False},
    },
    "category_neg2": {"item_lg": {"value": 500, "period": 52, "pos": False}},
}


def prep_budget(inner_budget, name="Some Budget", period=12, author=ObjectId()):
    """Prepare a budget, given its parts"""
    budget_dict = {
        "author": author,
        "name": name,
        "period": period,
        "budget": inner_budget,
    }
    return Budget(**budget_dict)


def test_prepare_budget_items_data():
    """Test the prepare_budget_items_data function"""
    budget = prep_budget(BUDGET_VARIED)
    item_data = budget_charts.prepare_budget_items_data(budget)
    assert item_data == {
        "item_lg": 1000,
        "item_lg (category_neg2)": 2166,
        "Other items (<2% of total)": 8,
    }


@pytest.mark.parametrize("positive", (True, False))
def test_inject_advice(positive, monkeypatch):
    """Test the inject_advice_function"""
    monkeypatch.setattr(budget_charts, "url_for", lambda x: None)
    advice = budget_charts.inject_advice(positive)
    if positive:
        assert "It looks like your income is greater than your spending." in advice
    else:
        assert "It looks like your spending is greater than your income." in advice

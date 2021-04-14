"""test_budget_helpers: test the finance.budget_helpers.py functions"""
import pytest
from bson.objectid import ObjectId

from src.routes.finance import budget_helpers
from src.routes.finance.models import Budget

SMALL_INNER_BUDGET = '{"cat": {"item": {"value": null, "period": 12, "pos": true}}}'
JSON_BUDGETS = [
    pytest.param(
        f"""{{"_id": {{"$oid": "6077496cdc39bc2f0ad1c595"}},
        "author": {{"$oid": "5eba1d8745b896e94fa6770a"}},
        "period": 12,
        "budget": {SMALL_INNER_BUDGET}}}""",
        id="all",
    ),
    pytest.param(
        '{"_id": {"$oid": "6077496cdc39bc2f0ad1c595"}}',
        id="minimal",
    ),
]


@pytest.mark.parametrize("json_budget", JSON_BUDGETS)
def test_json_to_budget(json_budget):
    """Test the json_to_budget function"""
    budget = budget_helpers.json_to_obj(json_budget)
    assert isinstance(budget, Budget)


def test_get_default_budget():
    """Test that the get_default_budget function gets a budget"""
    assert isinstance(budget_helpers.get_default_budget(), Budget)


BUDGET_INPUTS = [
    pytest.param(
        (SMALL_INNER_BUDGET, 52, "Some Budget", "6077496cdc39bc2f0ad1c595"),
        id="all",
    ),
    pytest.param(
        ({}, None, None, None),
        id="minimal",
    ),
]


@pytest.mark.parametrize("inputs", BUDGET_INPUTS)
def test_set_budget_object(inputs):
    """Test the set_budget_object function"""
    budget = budget_helpers.set_budget_object(*inputs)
    assert isinstance(budget, Budget)
    if inputs[1]:
        assert budget.period == inputs[1]
    if inputs[2]:
        assert budget.name == inputs[2]
    if inputs[3]:
        assert budget.id == ObjectId(inputs[3])
